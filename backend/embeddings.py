"""
Embeddings module using local sentence-transformers model (all-MiniLM-L6-v2).
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_embedding(text: str) -> np.ndarray:
    """Return a normalized embedding vector using local sentence-transformers."""
    embedding = model.encode(text, convert_to_numpy=True)
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm

