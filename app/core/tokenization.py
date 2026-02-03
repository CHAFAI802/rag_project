"""Utilities for loading and reusing Hugging Face tokenizers."""

from __future__ import annotations

import logging
from threading import Lock
from typing import Optional

from transformers import AutoTokenizer

from app.core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_tokenizers: dict[str, AutoTokenizer] = {}
_tokenizer_lock = Lock()


def get_tokenizer(model_name: Optional[str] = None) -> AutoTokenizer:
    """Return a cached tokenizer for the given model name."""

    name = model_name or EMBEDDING_MODEL
    if name not in _tokenizers:
        with _tokenizer_lock:
            if name not in _tokenizers:
                logger.info("Loading tokenizer: %s", name)
                _tokenizers[name] = AutoTokenizer.from_pretrained(name)
    return _tokenizers[name]


def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    """Return the number of tokens for the provided text."""

    if not text:
        return 0

    tokenizer = get_tokenizer(model_name)
    try:
        encoded = tokenizer.encode(text, add_special_tokens=False)
        return len(encoded)
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Tokenizer failed to encode text: %s", exc)
        return len(text.split())
