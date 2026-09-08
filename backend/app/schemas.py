from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class DocumentIn(BaseModel):
    content: str


class DocumentOut(BaseModel):
    id: int
    content: str
