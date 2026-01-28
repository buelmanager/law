# ✅ HuggingFace Spaces 배포 완료 체크리스트

## 📦 배포 준비 완료 항목

### ✅ 백엔드
- [x] FastAPI 앱 (main.py) - RAG 파이프라인 통합
- [x] 임베딩 모듈 (core/embeddings.py) - multilingual-e5-large
- [x] LLM 모듈 (core/llm.py) - llama-cpp-python 기반
- [x] 검색 모듈 (core/retriever.py) - 하이브리드 검색 (BM25 + 벡터)
- [x] API 엔드포인트
  - POST /api/chat - 채팅 RAG 엔드포인트 (SSE 스트리밍)
  - POST /api/search - 검색 엔드포인트
  - GET /api/health - 헬스 체크
- [x] requirements.txt - 모든 의존성 명시

### ✅ 프론트엔드
- [x] Next.js 14 App Router
- [x] ChatWindow 컴포넌트 (메시지, 출처, 면책 고지)
- [x] TypeScript + Tailwind CSS
- [x] SSE 스트리밍 응답 처리
- [x] 빌드 최적화 (npm run build)

### ✅ 데이터 & 벡터DB
- [x] 수집: law.go.kr API 클라이언트 (5개 노동법 샘플)
- [x] 처리: DocumentChunker (조항 기반 청크)
- [x] 인덱싱: ChromaDB 벡터DB 생성 완료
  - 5 documents indexed
  - Embeddings: 1024 dimensions
  - Path: ./vectordb (영구 저장)

### ✅ Docker & 배포
- [x] Dockerfile (멀티스테이지 빌드)
  - Node.js 20 빌더 → Next.js 빌드
  - Python 3.11 런타임 → FastAPI 실행
  - git 설치 (모델 다운로드용)
  - data/ 및 vectordb/ 포함
- [x] .dockerignore (최적화)
- [x] HEALTHCHECK 구성 (curl -f http://localhost:7860/api/health)
- [x] 환경 변수 설정 (PORT=7860, PYTHONUNBUFFERED=1)

### ✅ 배포 문서
- [x] DEPLOYMENT.md - 상세 배포 가이드
- [x] .env.example - 환경 변수 템플릿
- [x] README.md - 프로젝트 개요

---

## 🚀 HF Spaces 배포 단계

### 1단계: GitHub 리포지토리 준비
```bash
cd /Users/chulheewon/development/proj/law
git add .
git commit -m "Deploy: RAG-based Korean law chatbot ready for HF Spaces"
git push origin main
```

### 2단계: HuggingFace Spaces 생성
1. https://huggingface.co/spaces 접속
2. "Create new Space" 클릭
3. 설정값:
   - **Space name**: `korean-law-chatbot` (또는 선호하는 이름)
   - **Space SDK**: Docker
   - **Space hardware**: CPU (16GB RAM) - 중요!
   - **Repo type**: Public/Private
4. "Create Space" 클릭

### 3단계: GitHub 연결 (자동 배포)
1. Space 설정 → "Linked Repos" 
2. GitHub 계정 연결
3. 리포지토리 선택 및 동기화
4. 자동 배포 시작

### 4단계: 환경 변수 설정 (선택)
Space 설정 → "Environment variables"에서:
```
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-large
CHROMADB_PATH=./vectordb
LLM_MODEL_PATH=./models/qwen2.5-7b-instruct-q4_k_m.gguf
```

### 5단계: 배포 모니터링
- Space 상태: "Running" 될 때까지 기다림 (5-10분)
- 로그: "Build" 탭에서 실시간 확인
- 테스트: Space URL 접속 → 채팅 인터페이스 확인

---

## 🔍 배포 후 체크리스트

### 1️⃣ 기본 연결성
```bash
# Health Check
curl https://<USERNAME>-korean-law-chatbot.hf.space/api/health
# Expected: {"status": "healthy", "service": "law-chatbot-api", "version": "0.1.0"}
```

### 2️⃣ 채팅 기능
```bash
# POST /api/chat
curl -X POST https://<USERNAME>-korean-law-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "퇴직금은 어떻게 계산하나요?", "stream": false}'
```

### 3️⃣ 검색 기능
```bash
# POST /api/search
curl -X POST https://<USERNAME>-korean-law-chatbot.hf.space/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "퇴직금", "top_k": 3}'
```

### 4️⃣ 프론트엔드 UI
브라우저에서 `https://<USERNAME>-korean-law-chatbot.hf.space` 접속
- 채팅 입력창 확인
- 메시지 전송 테스트
- 응답 및 출처 표시 확인
- 면책 고지 확인

---

## 📊 배포 전 최종 확인

| 항목 | 상태 | 비고 |
|------|------|------|
| Dockerfile | ✅ | 멀티스테이지, git 포함, data/vectordb 복사 |
| requirements.txt | ✅ | 모든 의존성 명시 |
| Backend 코드 | ✅ | RAG 파이프라인 완성 |
| Frontend 코드 | ✅ | Next.js App Router 준비 |
| 벡터DB | ✅ | ChromaDB 5문서 인덱싱 완료 |
| 환경변수 | ✅ | .env.example 제공 |
| 문서 | ✅ | DEPLOYMENT.md + CLAUDE.md |
| .dockerignore | ✅ | 최적화된 빌드 크기 |

---

## 💡 주요 주의사항

1. **RAM**: HF Spaces CPU 16GB는 필수
   - Qwen2.5-7B (4-bit): ~4GB
   - multilingual-e5-large: ~2GB
   - ChromaDB + OS: ~4-6GB
   - **최소 요구**: 16GB

2. **첫 시작**: 모델 자동 다운로드 (2-3분, 첫 실행만)
   - Qwen2.5 GGUF 4-bit (~4GB)
   - multilingual-e5-large (~2GB)
   - 이후 캐시됨

3. **응답 시간**: 3-8초/질문
   - 검색: 0.5-1초
   - LLM 생성: 2-7초 (CPU 추론)

4. **벡터DB 영구성**: ./vectordb 디렉토리 포함
   - 배포 후 자동으로 사용됨
   - 새 문서 추가시 이미지 재빌드 필요

---

## 🆘 문제 해결

### 빌드 실패
- **원인**: npm ci 또는 pip install 실패
- **해결**: Dockerfile 로그 확인, requirements.txt 버전 확인

### 메모리 부족
- **증상**: "Killed" 또는 모델 로드 실패
- **해결**: HF Spaces 하드웨어를 "GPU-small" 이상으로 업그레이드

### 모델 다운로드 타임아웃
- **증상**: 첫 실행 후 60초 이상 응답 없음
- **해결**: 재시작 후 약 2-3분 대기 (모델 캐시 생성중)

### API 응답 400
- **확인**: 요청 형식이 JSON 형식인지 확인
- **예시**: `{"message": "질문", "stream": false}`

---

## 📈 다음 단계 (운영)

1. **더 많은 법률 데이터 추가**
   - `data/collect/` 확장 (대법원 판례, 행정해석 등)
   - `data/process/index_*.py` 실행
   - `vectordb/` 업데이트

2. **모델 업그레이드**
   - Qwen2.5-32B 또는 다른 모델 시도
   - 임베딩 모델 변경 (KoAlbert, KoBERT 등)

3. **모니터링 & 로깅**
   - HF Spaces 로그 확인
   - 사용자 피드백 수집

4. **성능 최적화**
   - 벡터DB 쿼리 최적화
   - LLM 프롬프트 튜닝
   - 캐싱 전략 추가

---

## 🎯 최종 상태

✅ **모든 준비 완료!**
- 코드: 완성 및 테스트
- 데이터: 5문서 인덱싱
- Docker: 배포 준비 완료
- 문서: 상세 가이드 제공

**다음: GitHub에 푸시 → HF Spaces 배포 진행**

---

*마지막 업데이트: 2024년*
