"""
Chat / RAG query endpoint.

POST /chat - takes a user question, retrieves the most relevant chunks
from the vector store, and generates a grounded answer using Gemini.
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services import vector_store, gemini_service

router = APIRouter(tags=["chat"])

TOP_K = 4  # how many chunks to retrieve as context
MAX_QUESTION_LENGTH = 1000  # basic abuse protection


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if len(question) > MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Question is too long (max {MAX_QUESTION_LENGTH} characters).",
        )

    # 1. Retrieve relevant chunks from the vector store
    try:
        retrieved = vector_store.query_similar_chunks(question, top_k=TOP_K)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error searching the knowledge base: {e}")

    # 2. Generate an answer grounded in those chunks
    try:
        answer = gemini_service.generate_answer(
            question=question,
            context_chunks=[c["text"] for c in retrieved],
        )
    except ValueError as e:
        # Config errors (e.g. missing API key) -> 400, not a 500 crash
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error calling Gemini API: {e}")

    # 3. Return the answer, but only cite the single most relevant source.
    # (We still used multiple chunks as context above for a better answer -
    # this just avoids showing weak/unrelated matches to the user.)
    best_match = retrieved[0] if retrieved else None
    sources = (
        [SourceChunk(filename=best_match["filename"], text=best_match["text"], distance=best_match["distance"])]
        if best_match
        else []
    )
    return ChatResponse(answer=answer, sources=sources)
