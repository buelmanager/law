# AI 법률 상담 챗봇 (RAG 기반)

한국 노동법 전문 AI 상담 챗봇으로, Retrieval-Augmented Generation (RAG) 기술을 활용하여 정확한 법률 정보를 제공합니다.

## 🚀 기술 스택

- **LLM**: Qwen2.5-7B-Instruct (GGUF 4-bit 양자화)
- **임베딩 모델**: multilingual-e5-large (다국어 지원)
- **백엔드**: FastAPI + Uvicorn
- **프론트엔드**: Next.js 14 App Router + TypeScript + Tailwind CSS
- **벡터DB**: ChromaDB
- **검색**: Hybrid Search (BM25 + 벡터 검색)
- **배포**: HuggingFace Spaces Docker

## 📋 주요 기능

1. **RAG 기반 법률 상담**: 데이터베이스의 법률 문서에서 관련 정보를 검색 후 LLM으로 답변 생성
2. **하이브리드 검색**: BM25 전문 검색과 의미 기반 벡터 검색 결합
3. **출처 표시**: 답변에 사용된 법률 조항 명시
4. **실시간 응답**: SSE(Server-Sent Events)를 통한 스트리밍 응답
5. **면책 고지**: 모든 답변에 법률 상담 지면책 포함

## 🏗️ 프로젝트 구조

```
law/
├── backend/                  # FastAPI 백엔드
│   ├── main.py              # 앱 진입점
│   ├── requirements.txt      # Python 의존성
│   ├── api/
│   │   ├── chat.py          # 채팅 API 엔드포인트
│   │   └── search.py        # 검색 API 엔드포인트
│   └── core/
│       ├── embeddings.py    # 임베딩 모델 관리
│       ├── llm.py           # LLM 추론
│       ├── retriever.py     # 벡터DB + 검색 로직
│       └── prompts.py       # 프롬프트 템플릿
├── frontend/                # Next.js 프론트엔드
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── src/
│       ├── app/             # App Router 페이지
│       └── components/      # React 컴포넌트
├── data/                    # 법률 데이터
│   ├── collect/            # 수집 스크립트
│   ├── process/            # 처리 및 인덱싱
│   └── raw/                # 원본 데이터
├── vectordb/               # ChromaDB 벡터 저장소 (영구)
├── models/                 # LLM 모델 캐시 (자동 다운로드)
└── Dockerfile              # HF Spaces 배포용
```

## 🔄 API 엔드포인트

### 1. 채팅 (RAG)
**POST** `/api/chat`

```json
{
  "message": "퇴직금은 어떻게 계산하나요?",
  "stream": true
}
```

응답 (SSE):
```json
{"type": "message", "content": "..."}
{"type": "sources", "content": [{"title": "근로자퇴직급여보장법", "text": "..."}]}
```

### 2. 검색
**POST** `/api/search`

```json
{
  "query": "퇴직금",
  "top_k": 5
}
```

### 3. 헬스 체크
**GET** `/api/health`

```json
{
  "status": "healthy",
  "service": "law-chatbot-api",
  "version": "0.1.0"
}
```

## 💻 로컬 개발

### 사전 요구사항
- Python 3.11+
- Node.js 20+
- 8GB 이상 RAM (권장: 16GB)

### 설치 및 실행

```bash
# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 백엔드 의존성 설치
pip install -r backend/requirements.txt

# 프론트엔드 의존성 설치
cd frontend && npm install && cd ..

# 프론트엔드 빌드
cd frontend && npm run build && cd ..

# 서버 실행 (포트 7860)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 7860 --reload
```

브라우저에서 `http://localhost:7860` 접속

## 🐳 Docker 배포 (HF Spaces)

### 빌드
```bash
docker build -t law-chatbot:latest .
```

### 로컬 테스트
```bash
docker run -p 7860:7860 law-chatbot:latest
```

### HuggingFace Spaces 배포

1. [HuggingFace Spaces](https://huggingface.co/spaces) 접속
2. "Create new Space" 클릭
3. 설정:
   - **Space name**: `law-chatbot` (또는 원하는 이름)
   - **Space SDK**: Docker
   - **Space hardware**: CPU (16GB RAM)
   - **Repository visibility**: Public/Private 선택
4. GitHub 리포지토리 연결 후 푸시
5. 자동 배포 시작 (약 5-10분)

### 환경 변수 (HF Spaces 설정)

Space 설정 → "Environment variables" 에서 추가:

```
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-large
CHROMADB_PATH=./vectordb
LLM_MODEL_PATH=./models/qwen2.5-7b-instruct-q4_k_m.gguf
HF_TOKEN=<your_hf_token>  # 선택사항: 모델 다운로드시
```

## 📊 성능 특성

| 항목 | 값 |
|------|-----|
| **응답 시간** | 3-8초 (검색 + LLM 생성) |
| **모델 크기** | Qwen2.5-7B 4-bit (~4GB) |
| **임베딩 차원** | 1024 |
| **벡터DB** | ChromaDB (영구 저장소) |
| **메모리 사용** | ~10-12GB (권장 16GB) |

## ⚖️ 면책 고지

이 챗봇은 **교육 및 정보 제공 목적**으로만 사용됩니다.

- ❌ 법적 구속력이 없습니다
- ❌ 전문 변호사 상담을 대체할 수 없습니다
- ✅ 일반적인 정보와 법령 내용 설명은 참고할 수 있습니다

**실제 법률 문제는 반드시 변호사와 상담하세요.**

## 🔄 데이터 업데이트

법률 데이터를 업데이트하려면:

1. `data/collect/` 에서 수집 스크립트 실행
2. `data/process/index_labor_laws.py` 로 재인덱싱
3. `vectordb/` 디렉토리 업데이트 후 이미지 재빌드

```bash
# 예시: 노동법 수집 및 인덱싱
python data/collect/collect_labor_laws.py
python data/process/index_labor_laws.py
```

## 📚 참고 자료

- [law.go.kr](https://www.law.go.kr) - 국가법령정보센터
- [Qwen2.5 모델](https://huggingface.co/Qwen)
- [ChromaDB 문서](https://docs.trychroma.com)
- [FastAPI 문서](https://fastapi.tiangolo.com)

## 📄 라이선스

MIT License

## 👨‍💻 개발자

AI 법률 상담 챗봇 - RAG 기반 한국 노동법 전문 시스템

---

**마지막 업데이트**: 2024년
