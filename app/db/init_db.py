from sqlalchemy import select, text

from app.core.security import hash_password
from app.db import models  # noqa: F401  (register models on metadata)
from app.db.base import Base
from app.db.models import User, UserRole
from app.db.session import SessionLocal, engine

TRIGGER_FUNC_SQL = """
CREATE OR REPLACE FUNCTION chunks_tsv_update() RETURNS trigger AS $$
BEGIN
  NEW.content_tsv := to_tsvector('english', coalesce(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

TRIGGER_DROP_SQL = "DROP TRIGGER IF EXISTS trg_chunks_tsv ON chunks;"

TRIGGER_CREATE_SQL = """
CREATE TRIGGER trg_chunks_tsv
BEFORE INSERT OR UPDATE ON chunks
FOR EACH ROW EXECUTE FUNCTION chunks_tsv_update();
"""


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text(TRIGGER_FUNC_SQL))
        conn.execute(text(TRIGGER_DROP_SQL))
        conn.execute(text(TRIGGER_CREATE_SQL))


def ensure_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == "admin@example.com"))
        if existing is None:
            db.add(
                User(
                    email="admin@example.com",
                    hashed_password=hash_password("admin123"),
                    full_name="Administrator",
                    role=UserRole.admin,
                )
            )
            db.commit()
    finally:
        db.close()