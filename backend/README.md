# Backend (FastAPI)

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
   Then open `.env` and paste in your free Gemini API key from
   https://aistudio.google.com/app/apikey

5. **Run the dev server** (once `main.py` is built out in Step 2):
   ```bash
   uvicorn app.main:app --reload
   ```
   API will be available at http://localhost:8000
   Interactive docs at http://localhost:8000/docs
