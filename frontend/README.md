# Frontend (Next.js)

The admin interface for managing the document knowledge base. The public
chat interface is added in Step 7.

## Local Setup

1. **Install dependencies** (from inside `frontend/`):
   ```powershell
   npm install
   ```

2. **Set up environment variables:**
   ```powershell
   copy .env.local.example .env.local
   ```
   The default (`http://localhost:8000`) already matches the backend's
   default port, so you usually won't need to change anything.

3. **Make sure the backend is running first** (see `../backend/README.md`),
   since the frontend calls it directly.

4. **Run the dev server:**
   ```powershell
   npm run dev
   ```
   Visit **http://localhost:3000**

## Pages

| Route | Purpose |
|---|---|
| `/` | Public chat interface — anyone can ask questions, no login required |
| `/login` | Sign in, or register a new account (admin accounts require the secret admin code set in the backend's `.env`) |
| `/admin` | Document catalog — upload, view status, and delete PDFs. Admin accounts only; redirects to `/login` otherwise. |

## Notes

- Auth token is stored in `localStorage` and sent as a `Bearer` token on
  every API request (see `lib/api.ts`).
- The admin dashboard polls `GET /documents` every 4 seconds so a
  document's status flips from "indexing" to "indexed" automatically.
