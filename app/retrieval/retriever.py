import uuid
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chunk, Document, User, UserRole
from app.retrieval.embedder import embed_query
from app.retrieval.hybrid import (
    keyword_search, reciprocal_rank_fusion, to_uuid, vector_search,
)
from app.retrieval.reranker import rerank


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    score: float
    chunk_index: int = 0


class Retriever:
    def __init__(self, db: Session):
        self.db = db

    def _allowed_document_ids(self, user):
        if user is None or user.role == UserRole.admin:
            return None
        role = user.role.value
        cond = or_(
            func.coalesce(func.array_length(Document.roles, 1), 0) == 0,
            Document.roles.any(role),
        )
        return self.db.execute(select(Document.id).where(cond)).scalars().all()

    def retrieve(self, query, user, top_k=None):
        top_k = top_k or settings.final_top_k
        allowed_ids = self._allowed_document_ids(user)

        # 1) Dense search (falls back to keyword-only if model unavailable)
        vec_hits = []
        try:
            qemb = embed_query(query)
            vec_hits = vector_search(self.db, qemb, settings.vector_top_k, allowed_ids)
        except Exception as e:
            print(f"[retriever] dense search skipped: {e}")

        # 2) Keyword (BM25-style) search
        kw_hits = keyword_search(self.db, query, settings.keyword_top_k, allowed_ids)

        vec_ids = [c.id for c, _ in vec_hits]
        kw_ids = [to_uuid(r["id"]) for r in kw_hits]

        fused = reciprocal_rank_fusion([vec_ids, kw_ids], settings.rrf_k)
        candidate_ids = [cid for cid, _ in fused[: settings.rerank_top_k]]
        if not candidate_ids:
            return []

        chunks = self.db.execute(
            select(Chunk).where(Chunk.id.in_(candidate_ids))
        ).scalars().all()
        chunk_map = {c.id: c for c in chunks}
        ordered = [chunk_map[cid] for cid in candidate_ids if cid in chunk_map]
        if not ordered:
            return []

        doc_ids = list({c.document_id for c in ordered})
        docs = self.db.execute(select(Document).where(Document.id.in_(doc_ids))).scalars().all()
        doc_titles = {d.id: d.title for d in docs}

        # 3) Cross-encoder rerank (falls back to fused order if unavailable)
        passages = [c.content for c in ordered]
        try:
            ranked = rerank(query, passages, top_k)
        except Exception as e:
            print(f"[retriever] reranker skipped: {e}")
            ranked = [(i, 1.0 / (i + 1)) for i in range(min(top_k, len(ordered)))]

        return [
            RetrievedChunk(
                chunk_id=ordered[idx].id,
                document_id=ordered[idx].document_id,
                document_title=doc_titles.get(ordered[idx].document_id, "Unknown"),
                content=ordered[idx].content,
                score=score,
                chunk_index=(ordered[idx].metadata_ or {}).get("index", 0),
            )
            for idx, score in ranked
        ]