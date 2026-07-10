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


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Retrieve relevant chunks from the vector store
    retrieved = vector_store.query_similar_chunks(question, top_k=TOP_K)

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

    # 3. Return the answer plus which sources it came from
    sources = [
        SourceChunk(filename=c["filename"], text=c["text"], distance=c["distance"])
        for c in retrieved
    ]
    return ChatResponse(answer=answer, sources=sources)
