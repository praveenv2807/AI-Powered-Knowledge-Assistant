import os
import traceback
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.api.deps import get_pipeline
from backend.rag.pipeline import KnowledgePipeline

router = APIRouter()
UPLOAD_DIR = os.path.join("backend", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    pipeline: KnowledgePipeline = Depends(get_pipeline)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Sanitize filename to avoid space or special character issues on Windows
    safe_filename = re.sub(r'[^a-zA-Z0-9_\.-]', '_', file.filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        # Index document into the pipeline
        stats = pipeline.load_documents([file_path])
        return {
            "message": f"Successfully processed {file.filename}",
            "stats": stats
        }
    except Exception as e:
        # Print detailed stack trace to terminal for quick debugging
        print("\n--- DETAILED UPLOAD ERROR ---")
        traceback.print_exc()
        print("-----------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))