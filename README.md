# FAQ RAG Chatbot

A full-stack FAQ chatbot with **Admin** and **User** interfaces, powered by a
Retrieval-Augmented Generation (RAG) pipeline.

## Stack

| Layer            | Technology                          |
|-------------------|--------------------------------------|
| Frontend           | Next.js (React)                     |
| Backend            | FastAPI (Python)                    |
| Vector Database     | ChromaDB (local, free)              |
| Embeddings          | sentence-transformers (local, free) |
| LLM                 | Google Gemini API (free tier)       |
| Auth                | JWT (role-based: admin / user)      |
| Dev Database        | SQLite → Supabase (Postgres) later  |

## Project Structure

```
faq-rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints (auth, documents, chat)
│   │   ├── services/      # RAG logic, embeddings, Gemini calls
│   │   ├── models/        # Pydantic + DB models
│   │   ├── utils/         # Helpers (PDF parsing, chunking)
│   │   └── main.py        # FastAPI app entrypoint
│   ├── data/
│   │   ├── uploads/       # Uploaded PDFs
│   │   └── chroma_db/     # Vector DB storage
│   ├── requirements.txt
│   └── .env.example
└── frontend/               # Next.js app (added in a later step)
```

## Build Progress

- [x] Step 1: Project scaffolding
- [x] Step 2: Backend skeleton (FastAPI health check + config)
- [ ] Step 3: Document ingestion pipeline (PDF → chunks → embeddings → ChromaDB)
- [ ] Step 4: RAG query endpoint (retrieve + Gemini answer generation)
- [ ] Step 5: Auth system (JWT, admin/user roles)
- [ ] Step 6: Admin interface (upload/manage documents)
- [ ] Step 7: User interface (chatbot UI)
- [ ] Step 8: Polish (citations, chat history, error handling)
- [ ] Step 9: Deployment (Vercel + Render/Railway)

## Getting Started (local dev)

See `backend/README.md` for backend setup instructions.
Frontend setup instructions will be added in Step 6/7.
