# AI Chatbot Sample

A sample AI chatbot project with RAG (Retrieval Augmented Generation), running on Docker Compose.

## Architecture

- **Frontend**: Next.js (App Router) + [Vercel AI SDK](https://sdk.vercel.ai/)'s `useChat` for streaming display
- **Backend**: FastAPI + PyTorch (Hugging Face Transformers) for text generation, Sentence-Transformers for embeddings
- **DB**: PostgreSQL + pgvector extension (`pgvector/pgvector` image) for vector search

```
frontend (Next.js, :3000)
   │  fetch (App Router API Route: /api/chat)
   ▼
backend (FastAPI, :8000)
   │  ① Embed the query (Sentence-Transformers)
   │  ② Search similar documents in pgvector (RAG)
   │  ③ Build a prompt and stream generation with a PyTorch model
   ▼
db (PostgreSQL + pgvector, :5432)
```

Chat responses are streamed token by token, and the frontend renders them in real time via the Vercel AI SDK's `useChat` (`streamProtocol: "text"`).

## Getting started

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (health check: `/health`)
- PostgreSQL: localhost:5432

On first startup, the backend takes a while to become ready because it downloads the PyTorch / Hugging Face models (downloaded models are cached in the `hf_cache` volume, so subsequent startups are faster).

## Registering documents for RAG

The chatbot answers using documents already stored in pgvector as reference context (if none are registered, it answers without any reference material).

```bash
curl -X POST http://localhost:8000/api/documents \
  -H "Content-Type: application/json" \
  -d '{"content": "This project is a sample chatbot built with Next.js, FastAPI, PyTorch, and pgvector."}'
```

List registered documents:

```bash
curl http://localhost:8000/api/documents
```

## Changing the models

These can be configured via `.env`:

| Variable | Description | Default |
|---|---|---|
| `EMBEDDING_MODEL` | Embedding model (Sentence-Transformers) | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| `EMBEDDING_DIM` | Embedding dimension (must match the DB schema) | `384` |
| `GENERATION_MODEL` | Generation model (Hugging Face causal LM) | `rinna/japanese-gpt2-small` |
| `RAG_TOP_K` | Number of documents to retrieve | `3` |
| `MAX_NEW_TOKENS` | Max number of tokens to generate | `200` |

The default `rinna/japanese-gpt2-small` uses a Japanese SentencePiece tokenizer (requires `sentencepiece` in `backend/requirements.txt`, loaded with `use_fast=False`). You can switch back to the English `gpt2` model if you prefer. If you change `EMBEDDING_MODEL` to one with a different dimension, update `VECTOR(384)` in `db/init.sql` accordingly.

> Note: `rinna/japanese-gpt2-small` is a base language model without instruction tuning, so while it can generate conversational text, it won't give precise, on-topic answers the way ChatGPT does. This project is primarily a technical demo of the RAG + streaming pipeline.

## Project structure

```
.
├── docker-compose.yml
├── db/
│   └── init.sql          # pgvector extension + table definitions
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py       # FastAPI entry point
│       ├── config.py
│       ├── db.py         # asyncpg + pgvector
│       ├── rag.py        # prompt construction
│       ├── schemas.py
│       ├── ml/
│       │   ├── embeddings.py  # Sentence-Transformers
│       │   └── generator.py   # PyTorch streaming generation
│       └── routers/
│           ├── chat.py
│           └── documents.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── app/
        ├── page.tsx           # chat UI (useChat)
        ├── layout.tsx
        └── api/chat/route.ts  # streaming proxy to the backend
```
