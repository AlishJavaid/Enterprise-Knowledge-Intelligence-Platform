from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_db, get_current_user
from app.db.models import User
from app.retrieval.retriever import Retriever

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
def search(
    q: str,
    top_k: int = 6,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results = Retriever(db).retrieve(q, user, top_k)
    return {
        "query": q,
        "results": [
            {
                "chunk_id": str(r.chunk_id),
                "document_id": str(r.document_id),
                "document_title": r.document_title,
                "content": r.content,
                "score": round(r.score, 4),
                "chunk_index": r.chunk_index,
            }
            for r in results
        ],
    }