import os
import re
import tempfile
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .ai_service import (
    generate_actual_topic_refusal,
    generate_panic_mode,
    generate_useless_lesson,
    generate_useless_questions,
)
from .importance_scorer import score_document
from .pdf_processor import process_pdf

APP_NAME = "Notes But Not The Notes API"
DEFAULT_MAX_UPLOAD_MB = 15
PDF_SIGNATURE = b"%PDF-"


def read_cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


def max_upload_bytes() -> int:
    try:
        max_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", str(DEFAULT_MAX_UPLOAD_MB)))
    except ValueError:
        max_mb = DEFAULT_MAX_UPLOAD_MB
    return max(1, max_mb) * 1024 * 1024


def safe_filename(filename: str) -> str:
    cleaned_name = Path(filename).name
    cleaned_name = re.sub(r"[^A-Za-z0-9._-]", "_", cleaned_name)
    return cleaned_name or "upload.pdf"


def is_pdf(filename: str, content: bytes) -> bool:
    return filename.lower().endswith(".pdf") and content.startswith(PDF_SIGNATURE)


app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=read_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def run_ai_generation(generator, *args, **kwargs) -> JSONResponse:
    try:
        result = generator(*args, **kwargs)
        return JSONResponse(content=result if isinstance(result, dict) else {"text": result})
    except RuntimeError as error:
        if "OPENAI_API_KEY" in str(error):
            raise HTTPException(status_code=503, detail=str(error)) from error
        raise HTTPException(status_code=502, detail="The useless academic assistant returned no usable response.") from error


@app.post("/api/ai/lesson")
async def generate_lesson(payload: dict[str, object]) -> JSONResponse:
    document = payload.get("document")
    if not isinstance(document, dict):
        raise HTTPException(status_code=400, detail="A structured document is required.")
    return run_ai_generation(generate_useless_lesson, document, str(payload.get("question", "Teach me this document.")))


@app.post("/api/ai/questions")
async def generate_questions(payload: dict[str, object]) -> JSONResponse:
    document = payload.get("document")
    if not isinstance(document, dict):
        raise HTTPException(status_code=400, detail="A structured document is required.")
    return run_ai_generation(generate_useless_questions, document)


@app.post("/api/ai/panic")
async def generate_panic(payload: dict[str, object]) -> JSONResponse:
    document = payload.get("document")
    if not isinstance(document, dict):
        raise HTTPException(status_code=400, detail="A structured document is required.")
    duration = payload.get("duration", "30 minutes")
    if not isinstance(duration, str) or duration not in {"2 hours", "1 hour", "30 minutes", "10 minutes"}:
        raise HTTPException(status_code=400, detail="Choose 2 hours, 1 hour, 30 minutes, or 10 minutes.")
    return run_ai_generation(generate_panic_mode, document, duration)


@app.post("/api/ai/refusal")
async def generate_refusal(payload: dict[str, object]) -> JSONResponse:
    document = payload.get("document")
    topic = payload.get("topic")
    if not isinstance(document, dict) or not isinstance(topic, str) or not topic.strip():
        raise HTTPException(status_code=400, detail="A structured document and topic are required.")
    return run_ai_generation(generate_actual_topic_refusal, document, topic)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.post("/api/score")
async def score_pdf_structure(document: dict[str, object]) -> JSONResponse:
    if not isinstance(document, dict) or not document:
        raise HTTPException(status_code=400, detail="A structured PDF document is required.")
    try:
        return JSONResponse(content=score_document(document))
    except (AttributeError, TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail="The PDF structure could not be scored.") from error


@app.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A PDF filename is required.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > max_upload_bytes():
        max_mb = max_upload_bytes() // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"PDF must be smaller than {max_mb} MB.")
    if not is_pdf(file.filename, content):
        raise HTTPException(status_code=415, detail="Only valid PDF files are accepted.")

    document_id = uuid.uuid4().hex
    upload_dir = Path(os.getenv("UPLOAD_DIR", Path(tempfile.gettempdir()) / "notes-but-not-the-notes"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / f"{document_id}_{safe_filename(file.filename)}"
    saved_path.write_bytes(content)

    try:
        document = process_pdf(content, safe_filename(file.filename), document_id)
    except Exception as error:
        saved_path.unlink(missing_ok=True)
        if isinstance(error, ValueError):
            raise HTTPException(status_code=422, detail=str(error)) from error
        raise HTTPException(status_code=422, detail="The PDF could not be processed.") from error

    return {
        "document_id": document_id,
        "filename": safe_filename(file.filename),
        "content_type": file.content_type or "application/pdf",
        "size_bytes": len(content),
        "stored": True,
        "document": document,
    }
