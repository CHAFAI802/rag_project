from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

result = client.sentence_similarity(
    "That is a happy person",
    [
        "That is a happy dog",
        "That is a very happy person",
        "Today is a sunny day"
    ],
    model="sentence-transformers/all-MiniLM-L6-v2",
)

print(result)
