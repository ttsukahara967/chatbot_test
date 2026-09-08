import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import settings
from app.db import insert_chat_message, search_similar_documents
from app.ml.embeddings import embed_text
from app.ml.generator import stream_generate
from app.rag import build_prompt
from app.schemas import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(payload: ChatRequest) -> StreamingResponse:
    user_messages = [m for m in payload.messages if m.role == "user"]
    query = user_messages[-1].content if user_messages else ""

    embedding = embed_text(query)
    contexts = await search_similar_documents(embedding, settings.top_k)
    prompt = build_prompt(query, contexts)

    await insert_chat_message("user", query)

    async def event_stream():
        loop = asyncio.get_event_loop()
        generator = stream_generate(prompt)
        full_response = ""
        while True:
            chunk = await loop.run_in_executor(None, next, generator, None)
            if chunk is None:
                break
            full_response += chunk
            yield chunk
        await insert_chat_message("assistant", full_response)

    return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8")
