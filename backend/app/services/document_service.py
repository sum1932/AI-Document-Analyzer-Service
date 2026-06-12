import uuid
from datetime import datetime
from typing import List, Optional
from app.services.document_parser import parse_file, parse_web_url, chunk_text
from app.services.embedding import get_embeddings
from app.services.vector_store import add_documents, search_similar, delete_collection, list_collections, get_collection_stats
from app.services.generator import generate_answer_with_sources
from app.core.config import settings


documents_db = {}


def upload_document(file_path: str, filename: str) -> dict:
    doc_id = str(uuid.uuid4())[:8]
    chunks = parse_file(file_path)
    chunked = chunk_text(chunks, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

    texts = [c.content for c in chunked]
    embeddings = get_embeddings(texts)

    chunk_dicts = [{"content": c.content, "metadata": c.metadata} for c in chunked]
    add_documents(doc_id, chunk_dicts, embeddings)

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
    documents_db[doc_id] = {
        "id": doc_id,
        "filename": filename,
        "doc_type": ext,
        "chunk_count": len(chunked),
        "created_at": datetime.now()
    }

    return documents_db[doc_id]


def upload_web_url(url: str) -> dict:
    doc_id = str(uuid.uuid4())[:8]
    chunks = parse_web_url(url)
    chunked = chunk_text(chunks, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

    texts = [c.content for c in chunked]
    embeddings = get_embeddings(texts)

    chunk_dicts = [{"content": c.content, "metadata": c.metadata} for c in chunked]
    add_documents(doc_id, chunk_dicts, embeddings)

    documents_db[doc_id] = {
        "id": doc_id,
        "filename": url,
        "doc_type": "web",
        "chunk_count": len(chunked),
        "created_at": datetime.now()
    }

    return documents_db[doc_id]


def get_documents() -> List[dict]:
    return list(documents_db.values())


def delete_document(doc_id: str) -> bool:
    if doc_id in documents_db:
        delete_collection(doc_id)
        del documents_db[doc_id]
        return True
    return False


def ask_question(question: str, document_ids: Optional[List[str]] = None) -> dict:
    target_ids = document_ids if document_ids else list(documents_db.keys())

    all_results = []
    for doc_id in target_ids:
        results = search_similar(doc_id, get_embeddings(question)[0], settings.TOP_K_RESULTS)
        all_results.extend(results)

    all_results.sort(key=lambda x: x.get("distance", float("inf")))

    top_results = all_results[:settings.TOP_K_RESULTS]

    return generate_answer_with_sources(question, top_results)
