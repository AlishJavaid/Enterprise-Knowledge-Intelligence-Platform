import re


def extract_citations(answer: str, contexts) -> list[dict]:
    refs = {int(m) for m in re.findall(r"\[(\d+)\]", answer)}
    citations = []
    for r in sorted(refs):
        if 1 <= r <= len(contexts):
            c = contexts[r - 1]
            citations.append(
                {
                    "index": r,
                    "document_id": str(c.document_id),
                    "document_title": c.document_title,
                    "chunk_id": str(c.chunk_id),
                    "snippet": c.content[:200],
                    "score": round(c.score, 4),
                }
            )
    return citations