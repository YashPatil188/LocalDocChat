import os
import requests
from typing import Dict

# Determine which LLM backend to use
USE_HF_INFERENCE = os.environ.get("USE_HF_INFERENCE", "0") == "1"

# --- HuggingFace Inference API config ---
HF_TOKEN = os.environ.get("HF_TOKEN", "")
# mistralai/Mistral-7B-Instruct-v0.3 and zephyr-7b are deprecated or experiencing routing issues
# Qwen/Qwen2.5-7B-Instruct is currently verified working
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# --- Ollama config (local) ---
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/") + "/api/generate"
MODEL_NAME = os.environ.get("LLM_MODEL", "tinyllama")


def _build_prompt(context: str, question: str) -> str:
    """Construct a focused prompt that works with multiple models."""
    if len(context) > 2000:
        context = context[:2000] + "..."

    prompt = (
        "You are a document assistant. Answer questions using ONLY the provided context. "
        "Be concise and direct. If the answer is not in the context, say "
        "'This information is not available in the uploaded documents.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    return prompt


def _generate_hf_inference(context: str, question: str) -> str:
    """Generate answer using HuggingFace Inference API via InferenceClient."""
    from huggingface_hub import InferenceClient
    
    if not HF_TOKEN:
        return "Error: HF_TOKEN environment variable is not set."

    client = InferenceClient(HF_MODEL, token=HF_TOKEN)
    messages = [
        {"role": "user", "content": _build_prompt(context, question)}
    ]
    
    try:
        response = client.chat_completion(messages, max_tokens=300, temperature=0.1)
        answer = response.choices[0].message.content.strip()
        return answer if answer else "No relevant answer found in the documents."
            
    except Exception as e:
        return f"HuggingFace API Error: {str(e)[:200]}"


def _generate_ollama(context: str, question: str) -> str:
    """Generate answer using local Ollama server."""
    payload: Dict = {
        "model": MODEL_NAME,
        "prompt": _build_prompt(context, question),
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


def generate_answer(context: str, question: str) -> str:
    """Call the configured LLM backend to generate an answer."""
    if USE_HF_INFERENCE:
        return _generate_hf_inference(context, question)
    else:
        return _generate_ollama(context, question)
