from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document, QueryLog


def get_dashboard_metrics(db: Session) -> dict:
    total_docs = db.scalar(select(func.count(Document.id))) or 0
    total_chunks = db.scalar(select(func.count(Chunk.id))) or 0
    total_queries = db.scalar(select(func.count(QueryLog.id))) or 0
    avg_latency = float(db.scalar(select(func.avg(QueryLog.latency_ms))) or 0)

    hallucinated = db.scalar(
        select(func.count(QueryLog.id)).where(QueryLog.hallucination_flag.is_(True))
    ) or 0
    hallucination_rate = (hallucinated / total_queries) if total_queries else 0.0

    day = func.date_trunc("day", QueryLog.created_at).label("day")
    rows = db.execute(
        select(day, func.count(QueryLog.id))
        .group_by(day)
        .order_by(day.desc())
        .limit(14)
    ).all()
    queries_per_day = [{"day": str(r[0].date()), "count": r[1]} for r in reversed(rows)]

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_queries": total_queries,
        "avg_latency_ms": round(avg_latency, 2),
        "hallucination_rate": round(hallucination_rate, 4),
        "queries_per_day": queries_per_day,
    }