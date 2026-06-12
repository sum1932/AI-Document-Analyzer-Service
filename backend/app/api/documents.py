from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.schemas import DocumentResponse, UploadResponse
from app.services.document_service import upload_document, upload_web_url, get_documents, delete_document


router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ["docx", "xlsx", "xls"]:
        raise HTTPException(status_code=400, detail="Only DOCX and Excel files are supported")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        doc = upload_document(temp_path, file.filename)
        return UploadResponse(
            document_id=doc["id"],
            filename=doc["filename"],
            chunk_count=doc["chunk_count"],
            message="Document uploaded and indexed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/url", response_model=UploadResponse)
async def upload_url(url: str):
    try:
        doc = upload_web_url(url)
        return UploadResponse(
            document_id=doc["id"],
            filename=doc["filename"],
            chunk_count=doc["chunk_count"],
            message="Web page indexed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    docs = get_documents()
    return [DocumentResponse(**d) for d in docs]


@router.delete("/{doc_id}")
async def delete_doc(doc_id: str):
    if delete_document(doc_id):
        return {"message": "Document deleted"}
    raise HTTPException(status_code=404, detail="Document not found")
