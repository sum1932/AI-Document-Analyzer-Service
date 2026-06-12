from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    doc_type: str
    chunk_count: int
    created_at: datetime


class ChatRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    message: str
