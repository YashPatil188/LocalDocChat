# Local Document Chat – Private AI Assistant

> Upload PDFs. Ask questions. Get answers from your documents — 100% locally, no cloud, no API keys.

---

## What This App Does

This is a web application that lets you **chat with your PDF documents** using a locally running AI model. Everything runs on your computer — your documents never leave your machine.

**Example usage:**
1. Upload a PDF (e.g., a company policy, a textbook, a manual)
2. Ask: *"What is the refund policy?"*
3. Get an answer sourced directly from the document

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite 5 + TailwindCSS 3 | Modern, responsive chat UI |
| **Backend** | FastAPI (Python) | REST API server |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Converts text to 384-dim vectors for similarity search |
| **LLM** | Qwen2.5:1.5b via Ollama | Generates answers from retrieved document chunks |
| **Vector DB** | FAISS (Facebook AI Similarity Search) | Stores and searches document embeddings |
| **PDF Parser** | PyMuPDF (fitz) | Extracts text from PDF files |

---

## How It Works (Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD FLOW                      │
│                                                             │
│  Upload PDF → Extract Text → Clean → Chunk (~600 tokens)   │
│       → Generate Embeddings → Store in FAISS Index          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    QUESTION ANSWERING FLOW                   │
│                                                             │
│  User Question → Embed Question → Search FAISS (top 3)     │
│       → Send Context + Question to Qwen2.5 → Display Answer│
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before running this app, you need three things installed on your computer:

### 1. Python 3.10 or newer
- Download from: https://www.python.org/downloads/
- During installation, **check "Add Python to PATH"**
- Verify: open a terminal and type `python --version`

### 2. Node.js 18 or newer
- Download from: https://nodejs.org/ (choose the LTS version)
- Verify: open a terminal and type `node --version`

### 3. Ollama (Local AI Model Runner)
- Download from: https://ollama.com/
- On Windows: run the installer (OllamaSetup.exe)
- On Mac: `brew install ollama`
- On Linux: `curl -fsSL https://ollama.com/install.sh | sh`
- Verify: open a terminal and type `ollama --version`

---

## Step-by-Step Setup Instructions

### Step 1: Download the AI Model (one-time, ~986 MB)

Open a terminal and run:
```bash
ollama pull qwen2.5:1.5b
```
Wait for the download to finish. You'll see `success` when it's done.

### Step 2: Install Backend Dependencies

Open a terminal in the project folder:
```bash
pip install -r backend/requirements.txt
```
This installs FastAPI, PyMuPDF, FAISS, sentence-transformers, etc.

> **Note:** The first time you start the backend, it will also download the embedding model (~80 MB). This only happens once.

### Step 3: Install Frontend Dependencies

Open another terminal in the project folder:
```bash
cd frontend
npm install
```
This installs React, Vite, TailwindCSS, and other frontend packages.

### Step 4: Start the Application

You need **3 terminals** running simultaneously:

**Terminal 1 — Ollama Server** (if not already running):
```bash
ollama serve
```
> On Windows, Ollama usually starts automatically. If you see "address already in use", it's already running — that's fine!

**Terminal 2 — Backend Server:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 3 — Frontend Server:**
```bash
cd frontend
npm run dev
```
Wait until you see: `VITE ready` and `Local: http://localhost:5173/`

### Step 5: Open the App

Open your browser and go to: **http://localhost:5173**

---

## How to Use the App

### Uploading Documents
1. Click the upload area or drag-and-drop PDF files onto it
2. Click **"Upload & Process"**
3. Wait for the success message (processing takes a few seconds depending on PDF size)
4. You can upload multiple PDFs — they all get indexed together

### Asking Questions
1. Type your question in the text box at the bottom
2. Press **Enter** or click the send button
3. Wait for the AI to respond (usually 5–15 seconds)
4. The answer will appear as a chat bubble on the left

### Tips for Best Results
- Ask **specific questions** about the document content
- Example: *"What are the key findings?"* instead of just *"what?"*
- The AI only uses information from your uploaded documents
- If the answer isn't in the documents, the AI will tell you

---

## API Endpoints

| Method | URL | Description | Request Body |
|--------|-----|-------------|--------------|
| `GET` | `/` | App info | — |
| `GET` | `/health` | Server status | — |
| `POST` | `/upload` | Upload PDFs | `multipart/form-data` with `files` field |
| `POST` | `/chat` | Ask a question | `{"question": "your question here"}` |

### Example API Calls (using curl/PowerShell):

**Health check:**
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok"}
```

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/upload -F "files=@document.pdf"
# Returns: {"detail": "Files processed successfully"}
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"question\": \"What is the main topic?\"}"
# Returns: {"answer": "The document discusses..."}
```

---

## Project Structure

```
local-document-chat/
│
├── backend/                    # Python FastAPI backend
│   ├── __init__.py             # Makes this a Python package
│   ├── main.py                 # FastAPI app, routes, CORS setup
│   ├── rag_pipeline.py         # Orchestrates upload & chat flows
│   ├── embeddings.py           # Text → vector embeddings (all-MiniLM-L6-v2)
│   ├── vector_store.py         # FAISS index: add, search, save, load
│   ├── llm.py                  # Ollama client (Qwen2.5:1.5b)
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React + Vite + TailwindCSS frontend
│   ├── index.html              # HTML entry point
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite config + proxy to backend
│   ├── tailwind.config.js      # TailwindCSS configuration
│   ├── postcss.config.js       # PostCSS plugins
│   └── src/
│       ├── main.jsx            # React entry point
│       ├── App.jsx             # Root layout component
│       ├── index.css           # Global styles + animations
│       └── components/
│           ├── Upload.jsx      # PDF upload with drag-and-drop
│           └── Chat.jsx        # Chat interface with message bubbles
│
├── data/                       # Auto-created: stores PDFs + FAISS index
├── Dockerfile                  # Docker deployment configuration
├── REPORT.md                   # Detailed technical report
└── README.md                   # This file
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ollama: command not found` | Install Ollama from https://ollama.com/ |
| `Cannot connect to Ollama` | Run `ollama serve` in a terminal |
| `Model not found` | Run `ollama pull qwen2.5:1.5b` |
| Backend won't start | Check Python is 3.10+: `python --version` |
| Frontend won't start | Check Node.js is 18+: `node --version` |
| `pip install` fails | Try: `pip install --upgrade pip` then retry |
| `npm install` fails | Try: `npm cache clean --force` then retry |
| Slow responses | Normal on CPU (5-15s). GPU makes it instant |
| Upload fails | Make sure the file is a valid PDF |
| Port 8000 in use | Kill the process: `npx kill-port 8000` |
| Port 5173 in use | Kill the process: `npx kill-port 5173` |

---

## Privacy & Security

- ✅ **All data stays on your machine** — PDFs are stored in `data/` folder
- ✅ **No cloud APIs** — embeddings and LLM inference are fully local
- ✅ **No telemetry** — zero external network calls
- ✅ **No account needed** — just run and use
- ✅ **FAISS index persists** — restart the app without re-uploading

---

## Docker Deployment (Optional)

```bash
# Build the image
docker build -t local-doc-chat .

# Run (make sure Ollama is accessible)
docker run -p 8000:8000 local-doc-chat
```

---

## License

MIT — free to use, modify, and distribute.
