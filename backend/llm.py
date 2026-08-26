import os
import requests
from typing import Dict

# --- Ollama config (local) ---
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/") + "/api/generate"
MODEL_NAME = os.environ.get("LLM_MODEL", "qwen2.5:1.5b")


def _build_prompt(context: str, question: str, history: list) -> str:
    """Construct a focused prompt that works with multiple models."""
    if len(context) > 2000:
        context = context[:2000] + "..."

    # Format last few messages of history (e.g. up to 4 messages for brevity)
    history_str = ""
    if history:
        for msg in history[-4:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_str += f"{role}: {msg.get('text', '')}\n"

    prompt = (
        "You are a document assistant. Answer the user's question using ONLY the provided context and the conversation history.\n"
        "Crucial rules for your answer:\n"
        "1. Be extremely concise, direct, and pinpoint. Provide ONLY the precise answer without any conversational filler, meta-commentary, introductory phrases, or unnecessary details.\n"
        "2. Do not repeat the context or the question.\n"
        "3. If the answer is not in the context, respond with: 'This information is not available in the uploaded documents.'\n\n"
        f"Context:\n{context}\n\n"
    )
    if history_str:
        prompt += f"Conversation History:\n{history_str}\n"

    prompt += (
        f"Question: {question}\n\n"
        "Answer:"
    )
    return prompt


def _generate_ollama(context: str, question: str, history: list) -> str:
    """Generate answer using local Ollama server."""
    payload: Dict = {
        "model": MODEL_NAME,
        "prompt": _build_prompt(context, question, history),
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 300,
            "num_ctx": 2048,
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
        return answer if answer else "No relevant answer found in the documents."
    except requests.exceptions.Timeout:
        return "The model is taking too long. Please try a shorter question."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Make sure it is running: open a terminal and run 'ollama serve'"
    except Exception as e:
        return f"Error: {str(e)}"


def generate_answer(context: str, question: str, history: list = None) -> str:
    """Call the local Ollama backend to generate an answer."""
    if history is None:
        history = []
    return _generate_ollama(context, question, history)

