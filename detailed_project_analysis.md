# Local Document Chat - Comprehensive Project Analysis

## 1. Project Overview

**Local Document Chat** is a robust, privacy-focused web application designed to allow users to chat directly with their PDF documents. By utilizing a Retrieval-Augmented Generation (RAG) pipeline, the application reads the provided documents, breaks them into digestible chunks, and uses advanced Language Models (LLMs) to accurately answer queries based strictly on the uploaded text.

A key feature of this application is its **Dual-Mode Architecture**, which allows it to seamlessly toggle between a 100% offline, privacy-first execution mode (using local models) and a lightweight cloud mode (tailored specifically for HuggingFace Spaces free-tier hosting).

---

## 2. Technical Stack

| Component | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite 5, TailwindCSS | Provides a modern, responsive user interface for PDF upload and chat. |
| **Backend Framework** | FastAPI (Python 3.10+) | Fast, async REST API layer. |
| **PDF Extraction** | PyMuPDF (`fitz`) | Robust, accurate text extraction from uploaded PDF documents. |
| **Embeddings Model** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Converts text chunks into 384-dimensional mathematical vectors for semantic search. |
| **Vector Database** | FAISS | Efficient, local, in-memory/on-disk vector storage for similarity search. |
| **LLM (Local Mode)** | Ollama (`tinyllama` / `Qwen2.5:1.5b`) | Runs the generative language model entirely on the local machine. |
| **LLM (Cloud Mode)**| HuggingFace Inference API (`Qwen/Qwen2.5-7B-Instruct`) | Offloads heavy LLM inference to the cloud to bypass local/container hardware limits. |

---

## 3. Architecture & Data Flow

### A. Document Upload Flow (Indexing)
1. **Upload**: User uploads one or multiple PDFs via the React frontend.
2. **Text Extraction**: The FastAPI endpoint (`/upload`) receives the files and processes them via `rag_pipeline.py`. `PyMuPDF` reads every page and compiles the raw text.
3. **Cleaning & Chunking**: The text is cleaned (removing excess whitespace) and chunked into ~600-token segments using a custom word-count chunker.
4. **Vector Embedding**: Each chunk is passed through the embedding model to generate a 384-dimension vector.
5. **Storage**: The chunks and their corresponding vectors are stored in a local FAISS index (`data/faiss_index.faiss`). **Note:** To maintain strict context, uploading new documents clears the previous FAISS index.

### B. Chat & Question Answering Flow (RAG)
1. **Query Input**: The user asks a question in the chat interface.
2. **Query Embedding**: The backend converts the user's question into an embedding using the identical embedding model.
3. **Similarity Search**: FAISS calculates the L2 distance between the question's vector and the document chunks' vectors, retrieving the top 3 most relevant chunks.
4. **Prompt Construction**: The backend (`llm.py`) constructs a strict prompt containing the context chunks and the user's question, commanding the LLM to answer *only* based on the context.
5. **Generation**: The prompt is routed to the active LLM (Ollama or HuggingFace), and the resulting text is streamed/sent back to the frontend to display to the user.

---

## 4. Deep Dive into Backend Modules

### `rag_pipeline.py` (The Orchestrator)
This module acts as the glue for the RAG pipeline. It defines the text cleaning and chunking algorithms. It exposes `process_upload` which manages the FAISS index (specifically wiping the old index on new uploads) and `handle_chat` which orchestrates vector search followed by LLM generation. 

### `llm.py` (The Generative Engine)
This file implements the Dual-Mode routing logic. Based on the `USE_HF_INFERENCE` environment variable, it decides whether to route the prompt to the HuggingFace API (using `huggingface_hub.InferenceClient`) or to the local Ollama server.
- **Local Error Handling**: It includes robust handling for connection errors and timeouts if Ollama isn't running or takes too long.
- **Prompt Engineering**: The core prompt forces the AI to output *"This information is not available in the uploaded documents."* if the query strays outside the provided context, significantly reducing AI hallucinations.

### `embeddings.py`
To solve major deployment issues (specifically Docker build size ceilings on HuggingFace Spaces), this module dynamically switches its embedding engine based on the `USE_ONNX` environment variable. 
- Local mode uses the heavy `sentence-transformers` library (PyTorch).
- Cloud mode downloads the ONNX-compiled version of the model and runs it via `onnxruntime`, reducing the container footprint by over 1GB while maintaining mathematical equivalence in the vectors.

### `vector_store.py`
A custom wrapper around FAISS. It manages creating new flat L2 indexes, appending vectors, and writing both the FAISS index and a companion JSON file (to store the raw text chunks) to the local disk in the `data/` directory.

### `main.py`
The FastAPI application wrapper. It configures CORS, serves static files for the React frontend (if built), and defines the REST API endpoints:
- `GET /health`
- `POST /upload`
- `POST /chat`
- `POST /reset` (Clears index and uploaded files)

---

## 5. Deployment and Containerization

The project ships with Dockerfiles configured for its two modes:
1. **Standard `Dockerfile`**: A multi-stage build that compiles the React app, bundles the FastAPI backend, and serves them together.
2. **`Dockerfile.hf`**: Specifically optimized for HuggingFace Spaces, completely omitting PyTorch and utilizing ONNX and HuggingFace Inference APIs.

### Overcoming Hardware Constraints
The project's architectural decisions—namely the `USE_ONNX` and `USE_HF_INFERENCE` toggles—were built to overcome the `cpu-basic` tier constraints (2 vCPU, 16GB RAM, 50GB storage) on HuggingFace Spaces. Offloading the model weights and inference allowed the app to run completely serverless without OOM (Out Of Memory) crashes or 10+ minute build time failures.

---

## 6. Privacy & Security Assurances
- **Fully Offline Capable**: In default mode, no API keys are required, and zero bytes of data are sent to external servers.
- **Stateless/Reset functionality**: Users can instantly wipe the vector DB and underlying PDF files from disk at any time, ensuring sensitive documents do not persist longer than needed.
