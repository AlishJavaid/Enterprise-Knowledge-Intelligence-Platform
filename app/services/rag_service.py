import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, QueryLog, User
from app.generation.citations import extract_citations
from app.generation.groundedness import check_groundedness
from app.generation.llm import get_llm
from app.generation.prompts import SYSTEM_PROMPT, build_rag_prompt
from app.retrieval.retriever import Retriever


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = Retriever(db)

    def _load_history(self, conversation_id):
        if not conversation_id:
            return []
        return (
            self.db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            .scalars()
            .all()
        )

    def answer(self, query: str, user: User, conversation_id=None) -> dict:
        t0 = time.perf_counter()

        history = self._load_history(conversation_id)
        contexts = self.retriever.retrieve(query, user)
        prompt = build_rag_prompt(query, contexts, history)
        answer = get_llm().generate(SYSTEM_PROMPT, prompt)

        citations = extract_citations(answer, contexts)
        confidence, hallucinated = check_groundedness(answer, contexts)
        latency_ms = (time.perf_counter() - t0) * 1000

        # Analytics
        self.db.add(
            QueryLog(
                user_id=user.id if user else None,
                query=query,
                retrieved_count=len(contexts),
                latency_ms=latency_ms,
                confidence=confidence,
                hallucination_flag=hallucinated,
            )
        )

        # Conversation memory
        if conversation_id:
            self.db.add(Message(conversation_id=conversation_id, role="user", content=query))
            self.db.add(
                Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    citations=citations,
                    latency_ms=latency_ms,
                )
            )

        self.db.commit()

        return {
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "hallucination_flag": hallucinated,
            "latency_ms": round(latency_ms, 2),
            "conversation_id": str(conversation_id) if conversation_id else None,
        }