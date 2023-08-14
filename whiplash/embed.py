import os

import requests

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"
API_KEY = None
headers = {"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"}


def embed(texts: list[str]):
    if not texts or len(texts) == 0:
        return []
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}},
    )
    data = response.json()
    if "error" in data:
        raise Exception("Error retreiving embeddings: ", data["error"], texts)
    return data


if __name__ == "__main__":
    texts = ["add(x, y)", "add(x, y) -> z"]
    print(embed(texts))
