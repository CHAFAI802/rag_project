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
    
    Args:
        context: Retrieved context from documents
        question: User question
        
    Returns:
        Generated answer
    """
    try:
        llm = get_llm()

        # Simple prompt for lightweight models
        prompt = f"""Context: {context}

Question: {question}

Answer:"""
        
        logger.debug(f"Generating answer for question: {question[:50]}...")
        result = llm(prompt)
        
        # Extract generated text
        if isinstance(result, list) and len(result) > 0:
            generated = result[0].get("generated_text", "")
            # Extract answer part (after "Answer:")
            answer = generated.split("Answer:")[-1].strip()
        else:
            answer = str(result)
        
        # Clean up
        if not answer or len(answer.strip()) == 0:
            answer = "Unable to generate answer from context"
        
        logger.debug(f"Answer generated: {answer[:100]}...")
        return answer
    except Exception as e:
        logger.error(f"Error generating answer: {e}", exc_info=True)
        # Fallback response
        return f"Answer based on provided context: {context[:200]}..."
