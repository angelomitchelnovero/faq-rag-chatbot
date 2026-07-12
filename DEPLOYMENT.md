# Deployment Guide

This deploys the app fully for free:

| Piece | Host | Why |
|---|---|---|
| Database + vector embeddings | **Supabase** (Postgres + pgvector) | Free, persistent, same one used in local dev |
| File storage (PDFs) | **Supabase Storage** | Free (1GB), persistent |
| Backend (FastAPI) | **Render** (free web service) | Free, runs a real Python server. Safe to be "stateless" now - restarts don't lose data, since everything lives in Supabase |
| Frontend (Next.js) | **Vercel** | Free, built for Next.js |

Because all persistent data lives in Supabase, the backend itself is
disposable - Render can restart/redeploy it anytime without losing
anything. This is what makes the free tiers actually usable for this.

---

## 1. Supabase (do this first)

Already covered in `backend/README.md` - create your project, and collect:
- `DATABASE_URL` (the Transaction pooler connection string)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

**Use this same project for local dev too** (fill these into your local
`.env`). Confirm it works locally first - run the backend, check
`http://localhost:8000/health` shows `database_connected: true` and
`pgvector_enabled: true` - before moving on to deployment.

### Keeping Supabase awake (free tier detail)

Supabase free projects pause after 7 days of *zero* database activity.
A simple free fix: a scheduled GitHub Action that pings your backend's
`/health` endpoint every few days, which touches the database and resets
the clock. A ready-to-use workflow is included at
`.github/workflows/keep-alive.yml` - it activates automatically once
you've deployed your backend and set one repository variable (see
step 4 below).

---

## 2. Backend on Render

1. Go to https://render.com and sign up (GitHub login is easiest)
2. **New -> Web Service** -> connect your `faq-rag-chatbot` GitHub repo
3. Configure:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
4. Add environment variables (Render dashboard -> your service -> **Environment**):

   | Key | Value |
   |---|---|
   | `GEMINI_API_KEY` | your Gemini key |
   | `JWT_SECRET_KEY` | a long random string (generate: `python -c "import secrets; print(secrets.token_hex(32))"`) |
   | `ADMIN_SIGNUP_CODE` | your own secret code |
   | `DATABASE_URL` | your Supabase pooler connection string |
   | `SUPABASE_URL` | your Supabase project URL |
   | `SUPABASE_SERVICE_ROLE_KEY` | your Supabase service role key |
   | `SUPABASE_STORAGE_BUCKET` | `documents` |
   | `FRONTEND_ORIGINS` | `["http://localhost:3000"]` for now - you'll update this in step 4 |

5. Click **Create Web Service**. First deploy takes a few minutes.
6. Once live, note your backend URL, e.g. `https://faq-rag-chatbot.onrender.com`
7. Visit `https://your-backend.onrender.com/health` - confirm
   `database_connected: true` and `pgvector_enabled: true`.

> **Free tier heads-up:** the service spins down after ~15 min of no
> traffic, so the first request after a quiet period takes 30-60 seconds
> to "wake up." Totally normal - just a one-time delay per idle period.

---

## 3. Frontend on Vercel

1. Go to https://vercel.com and sign up (GitHub login is easiest)
2. **Add New -> Project** -> import your `faq-rag-chatbot` repo
3. Configure:
   - **Root Directory:** `frontend`
   - Framework preset should auto-detect as Next.js
4. Add environment variable:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | your Render backend URL from step 2 (no trailing slash) |

5. Click **Deploy**.
6. Once live, note your frontend URL, e.g. `https://faq-rag-chatbot.vercel.app`

---

## 4. Connect them (CORS)

Your backend needs to know your real frontend URL is allowed to call it.

1. Back on Render, edit the `FRONTEND_ORIGINS` env var to:
   ```json
   ["https://your-app.vercel.app", "http://localhost:3000"]
   ```
   (keep `localhost:3000` too, so local dev against the deployed backend still works)
2. Save - Render will automatically redeploy with the new value.

### Enable the keep-alive workflow
In your GitHub repo -> **Settings -> Secrets and variables -> Actions -> Variables**,
add a repository variable:
   | Name | Value |
   |---|---|
   | `BACKEND_HEALTH_URL` | `https://your-backend.onrender.com/health` |

That's it - `.github/workflows/keep-alive.yml` will now ping it automatically.

---

## 5. Verify the deployed app

1. Visit your Vercel URL - you should see the chat interface
2. Click **ADMIN** -> register an account using your `ADMIN_SIGNUP_CODE`
3. Upload a PDF, confirm it shows **INDEXED**
4. Go back to the chat, ask a question about it - confirm you get a
   grounded answer with a source citation
5. Click **Download PDF** on the source - confirm it downloads
6. In the admin catalog, click **Edit** on the document, change the text,
   save - confirm the chat reflects the edit afterward

If anything fails, `https://your-backend.onrender.com/health` and the
Render service logs are the first places to check.
