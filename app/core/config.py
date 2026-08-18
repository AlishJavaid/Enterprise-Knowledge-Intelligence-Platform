from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Enterprise Knowledge Intelligence Platform"
    environment: str = "development"

    # Security
    secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/knowledge"

    # Models (Updated for Low-Memory ONNX Architecture)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    reranker_model: str = "none"  # Disabled heavy cross-encoder to save RAM

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Retrieval
    vector_top_k: int = 50
    keyword_top_k: int = 50
    rerank_top_k: int = 20
    final_top_k: int = 6
    rrf_k: int = 60

    # LLM
    llm_provider: str = "mock"  # openai | ollama | mock
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Uploads
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 100

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()