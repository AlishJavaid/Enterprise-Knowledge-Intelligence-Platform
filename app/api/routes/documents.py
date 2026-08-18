from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
import traceback

from app.core.config import settings
from app.core.security import get_db, get_current_user, require_roles
from app.db.models import Document, User, UserRole
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    roles: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    data = file.file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    role_list = [r.strip() for r in roles.split(",") if r.strip()]
    try:
        pipeline = IngestionPipeline(db)
        doc = pipeline.ingest_bytes(data, file.filename, ext, user.id, role_list)
    except Exception as e:
        # Catch the crash and return a clean error to the frontend
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(e)}")

    return {"id": str(doc.id), "title": doc.title, "chunks": doc.num_chunks, "status": doc.status.value}

@router.get("")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Document).order_by(Document.created_at.desc())
    if user.role != UserRole.admin:
        from sqlalchemy import func, or_
        stmt = stmt.where(
            or_(
                func.coalesce(func.array_length(Document.roles, 1), 0) == 0,
                Document.roles.any(user.role.value),
            )
        )
    docs = db.execute(stmt).scalars().all()
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "source_type": d.source_type,
            "status": d.status.value,
            "num_chunks": d.num_chunks,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]

@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}