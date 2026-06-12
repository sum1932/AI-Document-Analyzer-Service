import chromadb
from typing import List, Optional
from app.core.config import settings


client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def get_or_create_collection(name: str):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def add_documents(collection_name: str, chunks: List[dict], embeddings: List[List[float]]):
    collection = get_or_create_collection(collection_name)
    ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
    documents = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    return len(ids)


def search_similar(collection_name: str, query_embedding: List[float], top_k: int = 5) -> List[dict]:
    collection = get_or_create_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    result_list = []
    for i in range(len(results["ids"][0])):
        result_list.append({
            "id": results["ids"][0][i],
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if results["distances"] else None
        })
    return result_list


def list_collections() -> List[str]:
    return [c.name for c in client.list_collections()]


def delete_collection(name: str):
    client.delete_collection(name)


def get_collection_stats(name: str) -> dict:
    collection = get_or_create_collection(name)
    return {"count": collection.count()}
