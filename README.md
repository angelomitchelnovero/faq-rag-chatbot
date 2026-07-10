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
│   │   ├── routers/      # API endpoints (auth, documents, chat, health)
│   │   ├── services/      # RAG logic, embeddings, Gemini calls, auth
│   │   ├── models/         # DB models + Pydantic schemas
│   │   ├── utils/          # Helpers
│   │   ├── dependencies.py  # Auth guards (get_current_user, require_admin)
│   │   └── main.py          # FastAPI app entrypoint
│   ├── data/
│   │   ├── uploads/         # Uploaded PDFs
│   │   └── chroma_db/       # Vector DB storage
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── app/
    │   ├── page.tsx           # Public chat UI (root route)
    │   ├── login/               # Sign in / register page
    │   ├── admin/                # Admin dashboard (protected)
    │   └── layout.tsx             # Root layout, fonts, AuthProvider
    ├── lib/
    │   ├── api.ts                 # Backend API client
    │   └── auth.tsx                # Auth context (login state, token storage)
    ├── components/
    │   ├── ChatMessage.tsx          # Chat bubble with source citations
    │   ├── TypingIndicator.tsx       # "Assistant is typing" animation
    │   └── StatusBadge.tsx            # Document status chip (admin)
    └── .env.local.example
```

## Build Progress

- [x] Step 1: Project scaffolding
- [x] Step 2: Backend skeleton (FastAPI health check + config)
- [x] Step 3: Document ingestion pipeline (PDF → chunks → embeddings → ChromaDB)
- [x] Step 4: RAG query endpoint (retrieve + Gemini answer generation)
- [x] Step 5: Auth system (JWT, admin/user roles)
- [x] Step 6: Admin interface (upload/manage documents)
- [x] Step 7: User interface (chatbot UI)
- [x] Step 8: Polish (citations, chat history, error handling)
- [ ] Step 9: Deployment (Vercel + Render/Railway)

## Getting Started (local dev)

See `backend/README.md` for backend setup instructions.
Frontend setup instructions will be added in Step 6/7.
