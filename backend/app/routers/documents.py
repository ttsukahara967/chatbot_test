from fastapi import APIRouter

from app.db import insert_document, list_documents
from app.ml.embeddings import embed_text
from app.schemas import DocumentIn, DocumentOut

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentOut)
async def create_document(payload: DocumentIn) -> DocumentOut:
    embedding = embed_text(payload.content)
    doc_id = await insert_document(payload.content, embedding)
    return DocumentOut(id=doc_id, content=payload.content)


@router.get("", response_model=list[DocumentOut])
async def get_documents() -> list[DocumentOut]:
    rows = await list_documents()
    return [DocumentOut(**row) for row in rows]
