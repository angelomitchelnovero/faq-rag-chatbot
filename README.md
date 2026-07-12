# FAQ RAG Chatbot

A full-stack FAQ chatbot with **Admin** and **User** interfaces, powered by a
Retrieval-Augmented Generation (RAG) pipeline.

## Stack

| Layer            | Technology                                   |
|-------------------|-----------------------------------------------|
| Frontend           | Next.js (React) - deployed on Vercel          |
| Backend            | FastAPI (Python) - deployed on Render         |
| Database            | Supabase Postgres                             |
| Vector storage       | pgvector (Postgres extension, via Supabase)   |
| File storage          | Supabase Storage (PDFs)                       |
| Embeddings              | fastembed (local, ONNX, free, no API calls)  |
| LLM                       | Google Gemini API (free tier)             |
| Auth                        | JWT (role-based: admin / user)          |

All persistent data (users, documents, chunk embeddings, PDFs) lives in
Supabase - the backend itself holds no state, so it's safe to run on
free hosts with ephemeral disks (like Render's free tier) without losing
data on restart.

## Project Structure

```
faq-rag-chatbot/
├── DEPLOYMENT.md          # Full deployment walkthrough (Supabase + Render + Vercel)
├── .github/workflows/
│   └── keep-alive.yml       # Free scheduled ping to keep the Supabase project active
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints (auth, documents, chat, health)
│   │   ├── services/      # RAG logic, embeddings, Gemini calls, auth, storage
│   │   ├── models/         # DB models + Pydantic schemas
│   │   ├── utils/          # Helpers
│   │   ├── dependencies.py  # Auth guards (get_current_user, require_admin)
│   │   ├── database.py       # Postgres connection + pgvector setup
│   │   └── main.py            # FastAPI app entrypoint
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
    │   ├── EditDocumentModal.tsx     # Admin: view/edit a document's raw text
    │   ├── TypingIndicator.tsx        # "Assistant is typing" animation
    │   └── StatusBadge.tsx             # Document status chip (admin)
    └── .env.local.example
```

## Build Progress

- [x] Step 1: Project scaffolding
- [x] Step 2: Backend skeleton (FastAPI health check + config)
- [x] Step 3: Document ingestion pipeline (PDF → chunks → embeddings)
- [x] Step 4: RAG query endpoint (retrieve + Gemini answer generation)
- [x] Step 5: Auth system (JWT, admin/user roles)
- [x] Step 6: Admin interface (upload/manage documents)
- [x] Step 7: User interface (chatbot UI)
- [x] Step 8: Polish (citations, chat history, error handling)
- [x] Step 8.5: Admin can view/edit a document's raw text (re-indexes + regenerates the PDF)
- [x] Step 8.6: Migrated storage from local disk/ChromaDB to Supabase (Postgres/pgvector + Storage) for real persistence on free hosting
- [ ] Step 9: Deployment (Supabase + Render + Vercel) - see `DEPLOYMENT.md`

## Getting Started (local dev)

See `backend/README.md` and `frontend/README.md` for setup instructions.
See `DEPLOYMENT.md` when you're ready to deploy.
