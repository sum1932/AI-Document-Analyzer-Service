from fastapi import APIRouter
from typing import List, Optional
from app.models.schemas import ChatRequest, ChatResponse
from app.services.document_service import ask_question


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = ask_question(request.question, request.document_ids)
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
