# FastAPI backend

## Run locally

From the project root:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

Endpoints:

- `GET /health`
- `POST /api/upload` with a multipart field named `file`

Configuration is read from environment variables. See `.env.example`. The API currently checks the PDF extension and `%PDF-` file signature, saves the upload to a temporary directory, and returns a document ID. It does not call OpenAI or Supabase.

To enable the AI lesson, copy `backend/.env.example` to `backend/.env`, set `OPENAI_API_KEY` in that file, and restart the backend. The key is loaded server-side and is ignored by Git.
