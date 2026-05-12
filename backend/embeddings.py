"""
Embeddings module that supports both sentence-transformers (local) and ONNX Runtime (HF Spaces).
Set USE_ONNX=1 environment variable to use the lightweight ONNX backend.
"""
import os
import numpy as np

USE_ONNX = os.environ.get("USE_ONNX", "0") == "1"

if USE_ONNX:
    import onnxruntime as ort
    from tokenizers import Tokenizer
    from huggingface_hub import hf_hub_download

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    # Download ONNX model and tokenizer from HuggingFace Hub
    _onnx_path = hf_hub_download(repo_id=MODEL_NAME, filename="onnx/model.onnx")
    _tokenizer_path = hf_hub_download(repo_id=MODEL_NAME, filename="tokenizer.json")

    _session = ort.InferenceSession(_onnx_path)
    _tokenizer = Tokenizer.from_file(_tokenizer_path)
    _tokenizer.enable_padding(length=128)
    _tokenizer.enable_truncation(max_length=128)

    def get_embedding(text: str) -> np.ndarray:
        """Return a normalized embedding vector using ONNX Runtime."""
        encoded = _tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

        outputs = _session.run(None, {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        })

        # Mean pooling over token embeddings
        token_embeddings = outputs[0]  # (1, seq_len, hidden_dim)
        mask_expanded = attention_mask[:, :, np.newaxis].astype(np.float32)
        summed = np.sum(token_embeddings * mask_expanded, axis=1)
        counted = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        embedding = (summed / counted).flatten()

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

else:
    from sentence_transformers import SentenceTransformer

    # Load model once (global)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_embedding(text: str) -> np.ndarray:
        """Return a normalized embedding vector using sentence-transformers."""
        embedding = model.encode(text, convert_to_numpy=True)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
