"""Utilities for turning documents into retrieval-friendly chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Union


TokenCounter = Callable[[str], int]


@dataclass(frozen=True)
class ChunkMetadata:
    """Represents a chunk with position and token count metadata."""

    text: str
    start: int
    end: int
    tokens: int
    source: Optional[str] = None


_SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_paragraphs(text: str) -> List[tuple[str, int, int]]:
    """Split text into paragraphs preserving start/end offsets."""

    normalized = _normalize_newlines(text)
    paragraphs = []
    cursor = 0
    for block in normalized.split("\n\n"):
        cleaned = block.strip()
        if not cleaned:
            cursor += len(block) + 2  # account for delimiter length
            continue

        start = normalized.find(cleaned, cursor)
        if start == -1:
            start = cursor
        end = start + len(cleaned)
        paragraphs.append((cleaned, start, end))
        cursor = end
    return paragraphs


def _split_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into sentences while keeping punctuation."""

    sentences = _SENTENCE_SPLIT_REGEX.split(paragraph)
    # If regex fails (single long block), fall back to paragraph itself
    if len(sentences) == 1:
        return [paragraph]
    return [s.strip() for s in sentences if s.strip()]


def _segment_text(text: str) -> List[tuple[str, int, int]]:
    """Create sentence-level segments with offsets."""

    segments: List[tuple[str, int, int]] = []
    if not text:
        return segments

    normalized = _normalize_newlines(text)
    for paragraph, para_start, para_end in _split_paragraphs(normalized):
        running = para_start
        for sentence in _split_sentences(paragraph):
            if not sentence:
                continue
            sent_start = normalized.find(sentence, running, para_end)
            if sent_start == -1:
                sent_start = running
            sent_end = sent_start + len(sentence)
            segments.append((sentence, sent_start, sent_end))
            running = sent_end
    return segments


def _split_long_segment(
    segment: str,
    segment_start: int,
    measure: Callable[[str], int],
    chunk_size: int,
) -> List[tuple[str, int, int]]:
    """Break an oversized segment into smaller windows using whitespace."""

    words = segment.split()
    if not words:
        return []

    sub_segments: List[tuple[str, int, int]] = []
    current_words: List[str] = []
    current_start = segment_start
    tokens = 0

    for word in words:
        tentative_tokens = tokens + measure(word)
        if tentative_tokens > chunk_size and current_words:
            sub_text = " ".join(current_words)
            sub_end = current_start + len(sub_text)
            sub_segments.append((sub_text, current_start, sub_end))
            current_words = [word]
            current_start = sub_end + 1
            tokens = measure(word)
            continue
        current_words.append(word)
        tokens = tentative_tokens

    if current_words:
        sub_text = " ".join(current_words)
        sub_end = current_start + len(sub_text)
        sub_segments.append((sub_text, current_start, sub_end))

    return sub_segments


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    *,
    token_counter: Optional[TokenCounter] = None,
    min_chunk_tokens: int = 40,
    return_metadata: bool = False,
) -> Union[List[str], List[ChunkMetadata]]:
    """Chunk text with semantic awareness and optional metadata.

    Args:
        text: Raw document content to split.
        chunk_size: Maximum chunk length (characters by default, tokens when
            token_counter is provided).
        overlap: Desired overlap between consecutive chunks (same unit as
            chunk_size).
        token_counter: Optional callable returning token counts for a string.
        min_chunk_tokens: Minimum length required to keep a chunk (same unit as
            chunk_size).
        return_metadata: When True, include offsets and token counts per chunk.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if token_counter is None:
        def measure(value: str) -> int:
            return len(value)
    else:
        measure = token_counter

    segments = _segment_text(text)
    if not segments:
        return []

    chunks: List[ChunkMetadata] = []
    current_segments: List[ChunkMetadata] = []
    current_tokens = 0

    for segment_text, seg_start, seg_end in segments:
        seg_tokens = measure(segment_text)
        if seg_tokens == 0:
            continue

        if seg_tokens > chunk_size:
            # Break oversized segments before continuing.
            oversized_parts = _split_long_segment(
                segment_text, seg_start, measure, chunk_size
            )
            for part_text, part_start, part_end in oversized_parts:
                part_tokens = measure(part_text)
                if part_tokens == 0:
                    continue
                segments.append((part_text, part_start, part_end))
            continue

        if current_tokens + seg_tokens > chunk_size and current_segments:
            chunk = _finalize_chunk(current_segments, text, current_tokens)
            if chunk.tokens >= min_chunk_tokens:
                chunks.append(chunk)

            # Prepare overlap for next chunk.
            current_segments, current_tokens = _prepare_overlap(
                current_segments, overlap
            )

        # Append current sentence to chunk.
        current_segments.append(
            ChunkMetadata(segment_text, seg_start, seg_end, seg_tokens)
        )
        current_tokens += seg_tokens

    if current_segments:
        chunk = _finalize_chunk(current_segments, text, current_tokens)
        if chunk.tokens >= min_chunk_tokens:
            chunks.append(chunk)

    if return_metadata:
        return chunks
    return [chunk.text for chunk in chunks]


def _finalize_chunk(
    segments: Sequence[ChunkMetadata],
    original_text: str,
    total_tokens: int,
) -> ChunkMetadata:
    """Combine segment list into a single chunk preserving offsets."""

    start = segments[0].start
    end = segments[-1].end
    chunk_text_value = original_text[start:end].strip()
    if not chunk_text_value:
        chunk_text_value = " ".join(segment.text for segment in segments)
    return ChunkMetadata(chunk_text_value, start, end, total_tokens)


def _prepare_overlap(
    segments: Sequence[ChunkMetadata], overlap: int
) -> tuple[List[ChunkMetadata], int]:
    if overlap == 0 or not segments:
        return [], 0

    retained: List[ChunkMetadata] = []
    tokens_acc = 0
    for segment in reversed(segments):
        tokens_acc += segment.tokens
        retained.insert(0, segment)
        if tokens_acc >= overlap:
            break
    return retained, sum(segment.tokens for segment in retained)


def chunk_documents(
    docs: Iterable[str],
    chunk_size: int = 500,
    overlap: int = 100,
    *,
    token_counter: Optional[TokenCounter] = None,
    min_chunk_tokens: int = 40,
    return_metadata: bool = False,
    sources: Optional[Iterable[str]] = None,
) -> Union[List[str], List[ChunkMetadata]]:
    """Chunk a collection of documents, optionally attaching source metadata."""

    all_chunks: List[ChunkMetadata] = []
    sources_list = list(sources) if sources is not None else None

    for idx, doc in enumerate(docs):
        if not doc:
            continue
        source = sources_list[idx] if sources_list and idx < len(sources_list) else None
        chunks = chunk_text(
            doc,
            chunk_size=chunk_size,
            overlap=overlap,
            token_counter=token_counter,
            min_chunk_tokens=min_chunk_tokens,
            return_metadata=True,
        )
        if source:
            chunks = [ChunkMetadata(c.text, c.start, c.end, c.tokens, source) for c in chunks]
        all_chunks.extend(chunks)

    if return_metadata:
        return all_chunks
    return [chunk.text for chunk in all_chunks]
