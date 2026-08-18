import uuid

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chunk


def vector_search(db: Session, query_emb, top_k: int, allowed_doc_ids=None):
    stmt = (
        select(Chunk, Chunk.embedding.cosine_distance(query_emb).label("distance"))
        .order_by("distance")
        .limit(top_k)
    )
    if allowed_doc_ids is not None:
        stmt = stmt.where(Chunk.document_id.in_(allowed_doc_ids))
    return db.execute(stmt).all()


def keyword_search(db: Session, query: str, top_k: int, allowed_doc_ids=None):
    sql = """
        SELECT c.id AS id,
               ts_rank_cd(c.content_tsv, plainto_tsquery('english', :q)) AS rank
        FROM chunks c
        WHERE c.content_tsv @@ plainto_tsquery('english', :q)
    """
    params: dict = {"q": query, "lim": top_k}
    if allowed_doc_ids is not None:
        sql += " AND c.document_id = ANY(:doc_ids)"
        params["doc_ids"] = [str(d) for d in allowed_doc_ids]
    sql += " ORDER BY rank DESC LIMIT :lim"
    return db.execute(text(sql), params).mappings().all()


def reciprocal_rank_fusion(rankings: list[list], k: int = 60):
    """Fuse multiple ranked lists into one via RRF."""
    scores: dict = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def to_uuid(value):
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))