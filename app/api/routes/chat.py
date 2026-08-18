from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_db, get_current_user
from app.db.models import Conversation, Message, User
from app.schemas import ChatRequest, ConversationCreate
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/conversations")
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = Conversation(user_id=user.id, title=payload.title)
    db.add(conv)
    db.commit()
    return {"id": str(conv.id), "title": conv.title}


@router.post("/chat")
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return RAGService(db).answer(payload.query, user, payload.conversation_id)


@router.get("/conversations/{conv_id}/messages")
def get_messages(
    conv_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    msgs = (
        db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at)
        )
        .scalars()
        .all()
    )
    return [
        {
            "role": m.role,
            "content": m.content,
            "citations": m.citations,
            "latency_ms": m.latency_ms,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]