# Backend (FastAPI)

All persistent data (users, documents, chunk embeddings, PDFs) lives in
**Supabase** (Postgres + Storage), not on local disk. Use the same
Supabase project for local dev as you'll use in production, so behavior
matches in both places.

## One-time Supabase setup

1. Create a free project at https://supabase.com (no credit card required)
2. Go to **Project Settings -> Database -> Connection string** and copy
   the **Transaction pooler** URI (port 6543)
3. Go to **Project Settings -> Data API** and copy the **Project URL**
4. Go to **Project Settings -> API Keys** and copy the **service_role** key
   (keep this secret - it's backend-only, never expose it to the frontend)

That's it - the app automatically enables the `pgvector` extension and
creates its tables/storage bucket the first time it starts up. 

## Local Setup

1. **Create a virtual environment** (from inside `backend/`):
   ```bash
   python -m venv venv
   ```

2. **Activate it:**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Fill in `DATABASE_URL`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`
   from the Supabase setup above, plus your free Gemini API key from
   https://aistudio.google.com/app/apikey

5. **Run the dev server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   API will be available at http://localhost:8000
   Interactive docs at http://localhost:8000/docs

   Check http://localhost:8000/health - it should show
   `database_connected: true` and `pgvector_enabled: true`. If not, double
   check your `DATABASE_URL`.

## Deployment (Render)

See the root `DEPLOYMENT.md` for the full deployment walkthrough.
