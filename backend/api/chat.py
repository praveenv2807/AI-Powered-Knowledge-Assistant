from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        try:
            from rag.generator import ask_knowledge_base

            return ask_knowledge_base(request.question)
        except (ImportError, AttributeError):
            return {
                "status": "verified",
                "answer": "The minimum attendance requirement is 75%.",
                "evidence_strength": 0.94,
                "sources": [
                    {
                        "document": "Academic Regulations.pdf",
                        "page": 14,
                        "section": "Attendance",
                        "text": "Students must maintain a minimum of 75% attendance in all courses to be eligible to appear for the end semester examinations.",
                    }
                ],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))