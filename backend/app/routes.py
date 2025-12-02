# routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import shutil
import os
from logging import getLogger

from app.schemas import ChatRequest, ChatResponse
from app.engine import create_index, get_chat_engine

logger = getLogger("policy_ai.routes")

router = APIRouter()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), company_id: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=500, detail=str(e))

    try:
        status = create_index(file_path, company_id)
        return {"status": "success", "message": status}
    except Exception as e:
        logger.exception("Indexing failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        engine = get_chat_engine(request.company_id)
        resp = engine.chat(request.question)
        # resp is the simple object returned by ChatEngine.chat()
        return {"answer": resp.response, "sources": getattr(resp, "sources", []), "confidence_score": getattr(resp, "score", None)}
    except Exception as e:
        logger.exception("Chat endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))
