import os
import shutil
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            from rag.ingest import process_document

            res = process_document(file_path)
        except (ImportError, AttributeError):
            res = {"note": "RAG ingestion interface pending"}

        return {
            "status": "success",
            "filename": file.filename,
            "rag_result": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))