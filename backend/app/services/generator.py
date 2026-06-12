import google.generativeai as genai
from typing import List
from app.core.config import settings


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_answer(question: str, context_chunks: List[dict]) -> str:
    context = "\n\n---\n\n".join([
        f"[문서: {c['metadata'].get('source', 'unknown')}]\n{c['content']}"
        for c in context_chunks
    ])

    prompt = f"""아래 문서 내용을 참고하여 질문에 답변해주세요.
문서에 없는 내용은 답변하지 마세요.

=== 문서 내용 ===
{context}

=== 질문 ===
{question}

=== 답변 ==="""

    response = model.generate_content(prompt)
    return response.text


def generate_answer_with_sources(question: str, context_chunks: List[dict]) -> dict:
    answer = generate_answer(question, context_chunks)

    sources = []
    seen = set()
    for chunk in context_chunks:
        source = chunk["metadata"].get("source", "unknown")
        if source not in seen:
            seen.add(source)
            sources.append({
                "source": source,
                "excerpt": chunk["content"][:200]
            })

    return {"answer": answer, "sources": sources}
