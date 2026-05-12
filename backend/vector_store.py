import os
import faiss
import numpy as np
import pickle


def clear_index(index_path: str):
    """Delete the FAISS index and metadata files to start fresh."""
    if os.path.exists(index_path):
        os.remove(index_path)
    meta_path = index_path + ".meta"
    if os.path.exists(meta_path):
        os.remove(meta_path)


def _load_index(index_path: str):
    """Load FAISS index and metadata (list of documents). If not exists, create new index."""
    if os.path.exists(index_path):
        # Load index
        index = faiss.read_index(index_path)
        # Load metadata
        meta_path = index_path + ".meta"
        with open(meta_path, "rb") as f:
            docs = pickle.load(f)
        return index, docs
    else:
        # Create a new index for L2 (or inner product) normalized vectors
        dim = 384  # all-MiniLM-L6-v2 embedding size
        # Using IndexFlatIP for inner product (cosine similarity after normalization)
        index = faiss.IndexFlatIP(dim)
        docs = []
        return index, docs


def _save_index(index, docs, index_path: str):
    """Persist FAISS index and document list to disk."""
    faiss.write_index(index, index_path)
    meta_path = index_path + ".meta"
    with open(meta_path, "wb") as f:
        pickle.dump(docs, f)


def add_documents(chunks: list[str], embeddings: list[np.ndarray], index_path: str):
    """Add a batch of document chunks and their embeddings to the FAISS store.
    The function loads (or creates) the index, adds vectors, updates metadata, and saves.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")
    index, docs = _load_index(index_path)
    # Ensure embeddings are numpy float32 and normalized
    vectors = np.vstack([emb.astype(np.float32) for emb in embeddings])
    # Add to index
    index.add(vectors)
    # Append documents metadata
    docs.extend(chunks)
    _save_index(index, docs, index_path)


def search_documents(query_emb: np.ndarray, k: int = 5, index_path: str = None):
    """Search the FAISS store for the top‑k most similar chunks.
    Returns a list of tuples ``(document_text, score)`` sorted by descending similarity.
    """
    if index_path is None:
        raise ValueError("index_path must be provided")
    index, docs = _load_index(index_path)
    if index.ntotal == 0:
        return []
    query_vec = query_emb.astype(np.float32).reshape(1, -1)
    distances, indices = index.search(query_vec, k)
    results = []
    for idx, score in zip(indices[0], distances[0]):
        if idx < 0 or idx >= len(docs):
            continue
        results.append((docs[idx], float(score)))
    # Sort by score descending (FAISS inner product already gives higher = more similar)
    results.sort(key=lambda x: x[1], reverse=True)
    return results
