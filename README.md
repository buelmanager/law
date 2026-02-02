---
title: Korean Law Chatbot
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Korean Law Chatbot

RAG 기반 한국 법률 상담 AI 챗봇 서비스

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HuggingFace Spaces (Docker)                  │
│                         Port 7860                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐     ┌─────────────────────────────────────┐  │
│   │  Next.js    │     │         FastAPI Backend             │  │
│   │  Static     │     │                                     │  │
│   │  (React)    │     │  ┌───────────┐  ┌───────────────┐  │  │
│   │             │────▶│  │ /api/chat │  │ /api/search   │  │  │
│   │  /out/*     │     │  └─────┬─────┘  └───────┬───────┘  │  │
│   └─────────────┘     │        │                │          │  │
│                       │        ▼                ▼          │  │
│                       │  ┌─────────────────────────────┐   │  │
│                       │  │       RAG Service           │   │  │
│                       │  │  (rag_service.py)           │   │  │
│                       │  └──────────┬──────────────────┘   │  │
│                       │             │                      │  │
│        ┌──────────────┼─────────────┼──────────────────┐   │  │
│        ▼              ▼             ▼                  ▼   │  │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │Embeddings│  │ Retriever │  │   LLM    │  │ Prompts  │  │  │
│  │ (e5-base)│  │(Hybrid)   │  │(Mistral) │  │          │  │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └──────────┘  │  │
│       │              │             │                      │  │
│       ▼              ▼             ▼                      │  │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐               │  │
│  │sentence- │  │ ChromaDB  │  │Mistral AI│               │  │
│  │transform │  │ + BM25    │  │   API    │               │  │
│  └──────────┘  └───────────┘  └──────────┘               │  │
│                       │                                   │  │
│                       ▼                                   │  │
│                 ┌───────────┐                             │  │
│                 │ ./vectordb│                             │  │
│                 │ (Persist) │                             │  │
│                 └───────────┘                             │  │
│                                                           │  │
└───────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology | Specification |
|-----------|-----------|---------------|
| **Backend** | FastAPI + Uvicorn | Python 3.11, Port 7860 |
| **Frontend** | Next.js 14 | React 18, Static Export |
| **Embeddings** | sentence-transformers | `intfloat/multilingual-e5-base` (768 dims) |
| **Vector DB** | ChromaDB | Persistent, Cosine similarity |
| **Search** | Hybrid | BM25 + Vector (alpha=0.5) |
| **LLM** | Mistral AI | `open-mixtral-8x7b` (Groq fallback) |
| **Deploy** | HuggingFace Spaces | Docker, 16GB RAM, Free tier |

## Project Structure

```
law/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── api/
│   │   ├── chat.py             # POST /api/chat
│   │   ├── search.py           # POST /api/search
│   │   └── download.py         # File download endpoint
│   └── core/
│       ├── embeddings.py       # sentence-transformers wrapper
│       ├── retriever.py        # ChromaDB + BM25 hybrid search
│       ├── llm.py              # Mistral/Groq multi-provider
│       ├── rag_service.py      # RAG pipeline orchestration
│       ├── prompts.py          # System prompts & templates
│       └── auto_indexer.py     # Fallback indexing on startup
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main chat page
│   │   │   └── layout.tsx      # Root layout
│   │   └── components/
│   │       ├── ChatWindow.tsx  # Chat UI container
│   │       ├── MessageBubble.tsx
│   │       └── Disclaimer.tsx
│   ├── package.json            # Next.js 14, React 18, Tailwind
│   └── next.config.js          # output: 'export'
│
├── data/
│   ├── collect/
│   │   ├── law_drf_client.py   # law.go.kr DRF API client
│   │   ├── collect_all_categories.py  # Multi-category collector
│   │   └── collect_labor_laws.py      # Labor law specific
│   └── process/
│       └── index_cases.py      # Chunking + Embedding + Indexing
│
├── web/                        # Landing page (Vercel)
│   ├── index.html
│   ├── contact.html
│   ├── styles.css
│   └── script.js
│
├── vectordb/                   # ChromaDB persistent storage
├── Dockerfile                  # Multi-stage build
└── README.md
```

## API Endpoints

### POST /api/chat

법률 상담 채팅

```bash
curl -X POST https://wonchulhee-korean-law-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "퇴직금 계산 방법을 알려주세요"}'
```

**Request**
```json
{
  "message": "string (max 2000 chars)",
  "conversation_id": "string (optional)"
}
```

**Response**
```json
{
  "conversation_id": "uuid",
  "answer": "답변 내용",
  "sources": ["판례 2020다12345", "법령해석례 2021-0001"],
  "disclaimer": "면책 고지문"
}
```

### POST /api/search

법률 정보 검색

```bash
curl -X POST https://wonchulhee-korean-law-chatbot.hf.space/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "부당해고", "limit": 5}'
```

### GET /api/health

서버 상태 확인

```json
{
  "status": "healthy",
  "version": "0.5.1",
  "build_id": "embeddings-fix",
  "modules": {
    "embeddings": true,
    "retriever": true,
    "llm": true
  }
}
```

## Core Modules

### Embeddings (`backend/core/embeddings.py`)

Local sentence-transformers 기반 임베딩 생성

```python
from backend.core.embeddings import EmbeddingsManager

embeddings = EmbeddingsManager(model_name="intfloat/multilingual-e5-base")
vector = embeddings.encode("퇴직금 계산")  # shape: (768,)
vectors = embeddings.encode_batch(["질문1", "질문2"])  # shape: (2, 768)
```

### Retriever (`backend/core/retriever.py`)

ChromaDB + BM25 하이브리드 검색

```python
from backend.core.retriever import Retriever

retriever = Retriever(chroma_db_path="./vectordb", collection_name="law_cases")

# Vector search only
results = retriever.retrieve(query_embedding, top_k=5)

# Hybrid search (recommended)
results = retriever.hybrid_search(
    query_embedding=embedding,
    query_text="퇴직금",
    top_k=5,
    alpha=0.5  # vector:BM25 weight ratio
)
```

**Hybrid Search Algorithm**
```
score = alpha * vector_similarity + (1 - alpha) * bm25_score
```

### LLM (`backend/core/llm.py`)

Multi-provider LLM (Mistral 우선, Groq 폴백)

```python
from backend.core.llm import LLMManager

llm = LLMManager(
    mistral_api_key="...",  # Primary
    groq_api_key="..."      # Fallback
)

# Sync generation
answer = llm.generate(prompt, max_tokens=1024, temperature=0.7)

# Streaming
for chunk in llm.stream_generate(prompt):
    print(chunk, end="")
```

### RAG Service (`backend/core/rag_service.py`)

통합 RAG 파이프라인

```python
from backend.core.rag_service import RAGService

rag = RAGService(
    embeddings_manager=embeddings,
    retriever=retriever,
    llm_manager=llm
)

result = rag.process(
    question="퇴직금 계산 방법",
    top_k=5,
    max_tokens=1024,
    category_filter="labor"  # labor, lease, consumer, traffic
)

print(result.answer)
print(result.sources)  # ["판례 2020다12345", ...]
print(result.disclaimer)
```

## Categories

4대 법률 분야 특화 검색

| Category ID | 분야 | Keywords |
|------------|------|----------|
| `labor` | 노동법 | 퇴직금, 해고, 임금, 연차, 근로계약 |
| `lease` | 임대차법 | 전세, 보증금, 계약갱신, 대항력 |
| `consumer` | 소비자보호법 | 환불, 청약철회, 제품하자, 약관 |
| `traffic` | 교통사고 | 과실비율, 손해배상, 보험금 |

## Data Pipeline

### 1. Collection (법제처 API)

```bash
python data/collect/collect_all_categories.py \
  --enable-category labor,lease,consumer,traffic \
  --max-items 30 \
  --detail-limit 60
```

**Data Sources**
- 법제처 국가법령정보 (law.go.kr/DRF)
- 판례, 법령해석례, 헌재결정례

### 2. Indexing

```bash
python data/process/index_cases.py --collection law_cases
```

- Chunking: 조문/판시사항/이유 단위
- Embedding: e5-base (768 dims)
- Storage: ChromaDB (cosine similarity)

## Development

### Local Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 7860

# Frontend (별도 터미널)
cd frontend
npm install
npm run dev
```

### Environment Variables

```bash
# Required (하나 이상)
MISTRAL_API_KEY=your_mistral_key
GROQ_API_KEY=your_groq_key

# Optional
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-base
CHROMADB_PATH=./vectordb
PORT=7860
```

### Build & Test

```bash
# Frontend build
cd frontend && npm run build

# Full Docker build
docker build -t law-chatbot .
docker run -p 7860:7860 -e MISTRAL_API_KEY=... law-chatbot
```

## Deployment

### HuggingFace Spaces

```bash
# GitHub → HF Spaces 연동
git remote add hf https://huggingface.co/spaces/wonchulhee/korean-law-chatbot
git push hf main
```

**HF Secrets 설정**
- `MISTRAL_API_KEY` 또는 `GROQ_API_KEY`
- `HF_TOKEN` (optional, for model downloads)

### Vercel (Landing Page)

```bash
cd web
npx vercel --prod
```

## URLs

| Service | URL |
|---------|-----|
| Chatbot | https://wonchulhee-korean-law-chatbot.hf.space |
| Landing | https://lawbot-public.vercel.app |
| Health | https://wonchulhee-korean-law-chatbot.hf.space/api/health |

## Performance

| Metric | Value |
|--------|-------|
| Embedding latency | ~100ms |
| Hybrid search | ~50-100ms |
| LLM generation | 3-8s |
| Total response | 5-15s |
| Model size (e5-base) | ~560MB |
| Container size | ~2-3GB |

## Disclaimer

본 서비스는 AI가 제공하는 일반적인 법률 정보이며, 정식 법률 자문이 아닙니다.
구체적인 사안은 반드시 변호사와 상담하세요.

## Version

- **Version**: 0.5.1
- **Build ID**: embeddings-fix
- **Build Date**: 2026-01-29

## License

MIT License

Data sourced from:
- 법제처 국가법령정보 (CC BY)
- 대법원 공개 판례
