import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/chatbot"
    )
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "384"))
    generation_model: str = os.getenv("GENERATION_MODEL", "llm-jp/llm-jp-3-1.8b-instruct")
    top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    max_new_tokens: int = int(os.getenv("MAX_NEW_TOKENS", "200"))
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]


settings = Settings()
