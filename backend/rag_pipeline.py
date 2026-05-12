import os
import shutil
from typing import List

import fitz  # PyMuPDF

from .embeddings import get_embedding
from .vector_store import add_documents, search_documents, clear_index
from .llm import generate_answer

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.faiss")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

CHUNK_SIZE_TOKENS = 600  # approximate

def clean_text(text: str) -> str:
    """Basic cleaning: strip, replace multiple spaces, remove non-printable chars."""
    import re
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_TOKENS) -> List[str]:
    """Very simple token-approximation chunker based on word count.
    Assumes ~1 token = 0.75 words.
    """
    words = text.split()
    approx_tokens_per_word = 0.75
    max_words = int(chunk_size / approx_tokens_per_word)
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

async def process_upload(files: List[object]):
    """Save uploaded PDFs, extract text, chunk, embed, and store in FAISS.
    CLEARS the old index first so only the current upload's documents are indexed.
    """
    # Clear old index and old PDF files
    clear_index(FAISS_INDEX_PATH)
    for f in os.listdir(DATA_DIR):
        if f.endswith(".pdf"):
            os.remove(os.path.join(DATA_DIR, f))

    for upload in files:
        # Save file
        file_path = os.path.join(DATA_DIR, upload.filename)
        with open(file_path, "wb") as f:
            content = await upload.read()
            f.write(content)

        # Extract text using PyMuPDF
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        cleaned = clean_text(full_text)
        chunks = chunk_text(cleaned)
        embeddings = [get_embedding(chunk) for chunk in chunks]
        add_documents(chunks, embeddings, index_path=FAISS_INDEX_PATH)

async def handle_chat(question: str) -> str:
    """Given a user question, retrieve relevant chunks and generate answer via LLM."""
    query_emb = get_embedding(question)
    results = search_documents(query_emb, k=3, index_path=FAISS_INDEX_PATH)
    if not results:
        return "No documents have been uploaded yet. Please upload a PDF first."
    context = "\n\n".join([doc for doc, _score in results])
    answer = generate_answer(context, question)
    return answer

def reset_all():
    """Clear the FAISS index and delete all uploaded PDFs."""
    clear_index(FAISS_INDEX_PATH)
    for f in os.listdir(DATA_DIR):
        if f.endswith(".pdf"):
            os.remove(os.path.join(DATA_DIR, f))
