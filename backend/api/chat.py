from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.api.deps import get_pipeline
from backend.rag.pipeline import KnowledgePipeline

router = APIRouter()

class ChatQuery(BaseModel):
    question: str

@router.post("/chat")
async def chat_endpoint(
    query: ChatQuery,
    pipeline: KnowledgePipeline = Depends(get_pipeline)
):
    try:
        response = pipeline.answer_question(query.question)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail="Please upload a document first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))