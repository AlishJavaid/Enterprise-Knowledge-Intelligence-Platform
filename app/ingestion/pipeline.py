import hashlib

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Chunk, Document, DocumentStatus
from app.ingestion.chunker import split_text
from app.ingestion.parsers import parse_document
from app.retrieval.embedder import embed_texts


class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db

    def ingest_bytes(
        self,
        data: bytes,
        filename: str,
        ext: str,
        owner_id,
        roles: list[str],
        metadata: dict | None = None,
    ) -> Document:
        text = parse_document(data, ext)
        doc = Document(
            title=filename,
            source_type=ext.lower().lstrip("."),
            owner_id=owner_id,
            roles=roles or [],
            metadata_=metadata or {},
            content_hash=hashlib.sha256(data).hexdigest(),
            status=DocumentStatus.processing,
        )
        self.db.add(doc)
        self.db.flush()

        chunks = split_text(text, settings.chunk_size, settings.chunk_overlap)
        contents = [c["content"] for c in chunks]
        embeddings = embed_texts(contents) if contents else []

        for i, (meta, emb) in enumerate(zip(chunks, embeddings)):
            self.db.add(
                Chunk(
                    document_id=doc.id,
                    content=meta["content"],
                    embedding=emb,
                    char_start=meta["char_start"],
                    char_end=meta["char_end"],
                    metadata_={"index": i},
                )
            )

        doc.num_chunks = len(chunks)
        doc.status = DocumentStatus.indexed
        self.db.commit()
        self.db.refresh(doc)
        return doc