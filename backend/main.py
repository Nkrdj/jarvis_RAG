"""
FastAPI Backend for RAG Chatbot
Endpoints: upload document, ask question, reset session
"""

import os
import shutil
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import RAGEngine

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (use Redis for production)
sessions: dict[str, RAGEngine] = {}


class QuestionRequest(BaseModel):
    session_id: str
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list
    session_id: str


@app.get("/")
def root():
    return {"status": "RAG Chatbot API is running", "version": "1.0.0"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    allowed = [".pdf", ".txt", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed)}"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        session_id = f"session_{len(sessions) + 1}"
        engine = RAGEngine(openai_api_key=api_key)
        chunk_count = engine.load_document(tmp_path)
        sessions[session_id] = engine

        return {
            "session_id": session_id,
            "filename": file.filename,
            "chunks": chunk_count,
            "message": f"Document processed into {chunk_count} chunks. Ready to chat!"
        }
    finally:
        os.unlink(tmp_path)


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the uploaded document."""
    engine = sessions.get(request.session_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a document first.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = engine.ask(request.question)

    return AnswerResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=request.session_id
    )


@app.delete("/reset/{session_id}")
async def reset_session(session_id: str):
    """Reset a session and clear document memory."""
    engine = sessions.get(session_id)
    if engine:
        engine.reset()
        del sessions[session_id]

    return {"message": "Session cleared successfully"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "active_sessions": len(sessions)}
