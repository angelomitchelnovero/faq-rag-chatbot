"""
Gemini LLM service.

Wraps calls to Google's Gemini API (free tier) using the official
google-genai SDK. Takes retrieved context chunks + a user question,
and generates a grounded answer.
"""
from google import genai
from google.genai import types

from app.config import settings

_client = None

MODEL_NAME = "gemini-2.5-flash"  # solid free-tier model as of mid-2026

SYSTEM_INSTRUCTION = """You are a helpful FAQ assistant. Answer the user's question using ONLY the
context provided below, which comes from the organization's own documents.

Rules:
- If the answer is fully contained in the context, answer clearly and concisely.
- If the context does not contain enough information to answer, say so honestly -
  do not make up an answer. Suggest the user contact support for further help.
- Do not mention "the context" or "the documents" explicitly in your answer -
  just answer naturally, as if you already knew this information.
- Keep answers concise and directly useful.
"""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Generate an answer to `question`, grounded in `context_chunks`."""
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        raise ValueError(
            "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )

    if not context_chunks:
        context_text = "(No relevant documents were found in the knowledge base.)"
    else:
        context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"

    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    return response.text.strip()
