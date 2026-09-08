import asyncpg
from pgvector.asyncpg import register_vector

from app.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    await register_vector(conn)


async def connect() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        init=_init_connection,
        min_size=1,
        max_size=5,
    )


async def disconnect() -> None:
    if _pool is not None:
        await _pool.close()


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool is not initialized")
    return _pool


async def insert_document(content: str, embedding: list[float]) -> int:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO documents (content, embedding) VALUES ($1, $2) RETURNING id",
        content,
        embedding,
    )
    return row["id"]


async def list_documents() -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT id, content FROM documents ORDER BY id DESC")
    return [dict(row) for row in rows]


async def search_similar_documents(embedding: list[float], top_k: int) -> list[str]:
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT content
        FROM documents
        ORDER BY embedding <=> $1
        LIMIT $2
        """,
        embedding,
        top_k,
    )
    return [row["content"] for row in rows]


async def insert_chat_message(role: str, content: str) -> None:
    pool = get_pool()
    await pool.execute(
        "INSERT INTO chat_messages (role, content) VALUES ($1, $2)",
        role,
        content,
    )
