from transformers import pipeline

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = pipeline(
            "text-generation",
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=300,
            temperature=0.0
        )
    return _llm


def generate_answer(context: str, question: str) -> str:
    llm = get_llm()

    prompt = f"""
You are a document assistant.
You MUST answer only using the context below.
If the answer is not in the context, say: "No information found."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    result = llm(prompt)[0]["generated_text"]
    return result.split("ANSWER:")[-1].strip()
