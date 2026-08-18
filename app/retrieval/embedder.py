import os
import logging
from functools import lru_cache
from typing import List
from fastembed import TextEmbedding

# FORCE offline mode to prevent ANY runtime downloads
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HARDCODE the lightweight model to prevent config overrides
MODEL_NAME = "BAAI/bge-small-en-v1.5"
CACHE_DIR = "/app/models"

@lru_cache(maxsize=None)
def get_embedder() -> TextEmbedding:
    logger.info(f"Loading embedding model {MODEL_NAME} from {CACHE_DIR}...")
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=CACHE_DIR)

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = get_embedder()
    all_embeddings = []
    batch_size = 32
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = list(model.embed(batch))
        all_embeddings.extend([emb.tolist() for emb in embeddings])
    return all_embeddings

def embed_query(text: str) -> List[float]:
    if not text or not text.strip():
        return []
    return embed_texts([text])[0]