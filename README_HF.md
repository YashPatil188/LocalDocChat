---
title: Local Document Chat
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Local Document Chat — Private AI Assistant

Upload PDFs and ask questions — powered by TinyLlama running inside the container.

## Features
- PDF upload with drag-and-drop
- AI-powered question answering (RAG pipeline)
- FAISS vector search for document retrieval
- Clean, modern chat interface

## Tech Stack
- **Frontend**: React + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **LLM**: TinyLlama via Ollama
- **Embeddings**: all-MiniLM-L6-v2
- **Vector DB**: FAISS
