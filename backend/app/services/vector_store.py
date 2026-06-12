from pinecone import Pinecone, ServerlessSpec
from typing import List
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)


def get_or_create_index():
    existing = [idx.name for idx in pc.list_indexes()]
    if settings.PINECONE_INDEX_NAME not in existing:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(settings.PINECONE_INDEX_NAME)


def add_documents(collection_name: str, chunks: List[dict], embeddings: List[List[float]]):
    index = get_or_create_index()
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{collection_name}_{i}",
            "values": embedding,
            "metadata": {"content": chunk["content"], **chunk["metadata"], "collection": collection_name}
        })
    index.upsert(vectors=vectors)
    return len(vectors)


def search_similar(collection_name: str, query_embedding: List[float], top_k: int = 5) -> List[dict]:
    index = get_or_create_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"collection": {"$eq": collection_name}}
    )
    result_list = []
    for match in results.matches:
        result_list.append({
            "id": match.id,
            "content": match.metadata.get("content", ""),
            "metadata": {k: v for k, v in match.metadata.items() if k != "content"},
            "distance": match.score
        })
    return result_list


def list_collections() -> List[str]:
    index = get_or_create_index()
    stats = index.describe_index_stats()
    collections = set()
    for vector_id in stats.get("namespaces", {}).keys():
        collections.add(vector_id)
    return list(collections) if collections else ["default"]


def delete_collection(name: str):
    index = get_or_create_index()
    index.delete(delete_all=True, namespace=name)


def get_collection_stats(name: str) -> dict:
    index = get_or_create_index()
    stats = index.describe_index_stats()
    count = stats.get("namespaces", {}).get(name, {}).get("vector_count", 0)
    return {"count": count}
