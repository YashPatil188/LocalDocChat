from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from typing import List

from .rag_pipeline import process_upload, handle_chat, reset_all

app = FastAPI()

# Allow frontend (localhost:5173) and any origin for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "Local Document Chat - Private AI Assistant",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "upload": "POST /upload",
            "chat": "POST /chat",
        },
        "frontend": "http://localhost:5173",
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    try:
        await process_upload(files)
        return {"detail": "Files processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(query: dict):
    # Expected JSON: {"question": "...", "history": [...]}
    question = query.get("question")
    history = query.get("history", [])
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' field")
    try:
        answer = await handle_chat(question, history)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset():
    """Clear all uploaded documents and the FAISS index."""
    try:
        reset_all()
        return {"detail": "All documents and index cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve built frontend static files if they exist (production mode)
_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_frontend_dist):
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
