import logging
from threading import Lock
from transformers import pipeline
from app.core.config import LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

_llm = None
_llm_lock = Lock()


def get_llm():
    """
    Get or create the LLM pipeline (singleton with thread-safety).
    
    Uses double-check locking pattern to avoid race conditions.
    """
    global _llm
    if _llm is None:
        with _llm_lock:
            if _llm is None:
                logger.info(f"Loading LLM: {LLM_MODEL}")
                try:
                    _llm = pipeline(
                        "text-generation",
                        model=LLM_MODEL,
                        max_new_tokens=LLM_MAX_TOKENS,
                        temperature=LLM_TEMPERATURE
                    )
                    logger.info("LLM loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load LLM: {e}")
                    raise
    return _llm


def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer based on context and question.
    Uses direct extraction/summarization for better accuracy with small models.
    
    Args:
        context: Retrieved context from documents
        question: User question
        
    Returns:
        Generated answer
    """
    try:
        logger.debug(f"Generating answer for question: {question[:50]}...")
        
        # Strategy 1: Try to extract a direct answer from context
        # Look for sentences that directly relate to the question
        sentences = context.replace("[Source", "\n[Source").split("\n")
        
        relevant_sentences = []
        question_keywords = set(question.lower().split())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or sentence.startswith("[Source"):
                continue
                
            # Score sentence relevance
            sentence_lower = sentence.lower()
            keyword_matches = sum(1 for kw in question_keywords if kw in sentence_lower)
            
            # Take sentences with at least 2 keyword matches
            if keyword_matches >= 2 and len(sentence) > 20:
                relevant_sentences.append(sentence)
        
        # If we have relevant sentences, use them directly
        if relevant_sentences:
            # Take up to 2 sentences for a concise answer
            answer = " ".join(relevant_sentences[:2])
            if not answer.endswith("."):
                answer += "."
            logger.debug(f"Extracted answer: {answer[:100]}...")
            return answer
        
        # Strategy 2: If extraction fails, use LLM but with very conservative settings
        try:
            llm = get_llm()
            
            # Ultra-simple prompt for distilgpt2
            prompt = f"Q: {question}\nContext: {context}\nA:"
            
            result = llm(
                prompt,
                max_new_tokens=100,
                temperature=0.1,
                top_p=0.9,
                repetition_penalty=2.5,
                do_sample=False
            )
            
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get("generated_text", "")
                answer = generated.split("A:")[-1].strip()
            else:
                answer = ""
            
            # Clean up
            answer = answer.replace("<|endoftext|>", "").strip()
            
            if answer and len(answer) > 5:
                # Limit to first sentence
                first_sentence = answer.split(".")[0] + "."
                logger.debug(f"Generated answer: {first_sentence[:100]}...")
                return first_sentence
        except Exception as llm_error:
            logger.warning(f"LLM generation failed: {llm_error}")
        
        # Fallback: Return best matching sentence from context
        if sentences:
            best_sentence = max(
                (s for s in sentences if len(s) > 20 and not s.startswith("[")),
                key=len,
                default="No relevant information found"
            )
            return best_sentence if best_sentence != "No relevant information found" else "Unable to find relevant information"
        
        return "Unable to find relevant information in the provided context"
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}", exc_info=True)
        return "Unable to generate answer. Please try again."
