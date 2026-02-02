# 🚀 HuggingFace Spaces 배포 진행 안내

## ✅ 모든 준비 완료!

**커밋**: `✨ Deploy: RAG-based Korean law chatbot ready for HF Spaces`
**상태**: GitHub main branch에 푸시 완료

---

## 📋 HuggingFace Spaces 배포 단계별 가이드

### Step 1️⃣: HuggingFace Spaces 새로운 Space 생성

1. https://huggingface.co/spaces 접속
2. **"Create new Space"** 클릭
3. 다음 정보 입력:
   - **Owner**: 본인의 HF 계정
   - **Space name**: `korean-law-chatbot` (또는 선호하는 이름)
   - **License**: MIT (또는 선택)
   - **Private**: 선택사항
   - **Space SDK**: **Docker** ⭐ (중요!)
   - **Space hardware**: **CPU (16GB RAM)** ⭐ (필수!)
4. **Create Space** 클릭

### Step 2️⃣: GitHub 리포지토리 연결 (자동 배포 설정)

1. Space 생성 후 **Settings** 탭 이동
2. **"Linked Repos"** 섹션 찾기
3. **GitHub** 계정 연결 (처음이면 OAuth 승인)
4. 리포지토리 선택: `.env` 파일의 `GITHUB_REPO_URL` 참조
5. **"Link"** 클릭

### Step 3️⃣: 자동 배포 시작

- GitHub 연결 후 **자동으로 빌드 시작** (약 2-3분 대기)
- **Logs** 탭에서 실시간 빌드 진행 상황 확인
- 다음 항목 확인:
  ```
  ✅ npm install (frontend)
  ✅ npm run build (Next.js)
  ✅ pip install (backend)
  ✅ Docker build complete
  ✅ Server started on port 7860
  ```

### Step 4️⃣: 환경 변수 설정 (선택사항)

Space Settings → **"Environment variables"**에서:

```
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-large
CHROMADB_PATH=./vectordb
LLM_MODEL_PATH=./models/qwen2.5-7b-instruct-q4_k_m.gguf
DEBUG=False
```

### Step 5️⃣: 첫 배포 완료 확인

- Space 상태가 **"Running"** 으로 표시될 때까지 대기 (총 5-15분)
- 모델 자동 다운로드 (첫 실행만, 약 2-3분 소요):
  - Qwen2.5-7B GGUF: ~4GB
  - multilingual-e5-large: ~2GB
- 로그에서 `"Server started"` 메시지 확인

---

## 🧪 배포 완료 후 테스트

### 1. 기본 연결성 확인

```bash
# Health Check (서버 상태 확인)
curl https://<USERNAME>-korean-law-chatbot.hf.space/api/health

# Expected Response:
{
  "status": "healthy",
  "service": "law-chatbot-api",
  "version": "0.1.0"
}
```

### 2. 채팅 API 테스트

```bash
# Chat Request (RAG 기반 답변)
curl -X POST https://<USERNAME>-korean-law-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "퇴직금은 어떻게 계산하나요?",
    "stream": false
  }'

# Expected Response:
{
  "answer": "퇴직금 계산에는...",
  "sources": [
    {
      "title": "근로자퇴직급여보장법",
      "text": "..."
    }
  ],
  "disclaimer": "⚠️ 이 답변은..."
}
```

### 3. UI 테스트

브라우저에서 접속:
```
https://<USERNAME>-korean-law-chatbot.hf.space
```

확인 항목:
- ✅ 채팅 입력창 표시
- ✅ 메시지 전송 버튼 작동
- ✅ AI 응답 실시간 스트리밍
- ✅ 출처 법령 표시
- ✅ 면책 고지 표시

---

## 📊 배포 상태 모니터링

### Logs 탭에서 확인할 항목

```
# 성공한 빌드 로그 예시
Step 1/N: FROM node:20-slim as frontend-builder
...
Step N: CMD ["python", "-m", "uvicorn", "backend.main:app", ...]
Successfully tagged <image>:latest
...
Server started on port 7860
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### 실패 시 확인사항

| 증상 | 해결 방법 |
|------|---------|
| `Build failed` | Logs 탭에서 에러 메시지 확인 → Docker는 필수 |
| `Out of memory` | 하드웨어를 GPU-small 이상으로 업그레이드 |
| `ModuleNotFoundError` | requirements.txt 의존성 확인 |
| `Model download timeout` | 재시작 후 2-3분 대기 (처음 실행만) |

---

## 🔄 코드 업데이트 후 자동 재배포

GitHub에 새로운 커밋을 푸시하면 자동으로 다시 빌드됩니다:

```bash
# 예시: 더 많은 법률 데이터 추가
git add .
git commit -m "Add: More labor law data (industry safety, etc)"
git push origin main

# → HF Spaces에서 자동 감지 → 자동 재빌드 시작
```

---

## 📈 향후 운영 계획

### 1단계: 초기 배포 (지금)
- [x] Docker 이미지 준비
- [x] GitHub 저장소 준비
- [ ] HF Spaces 배포 진행 ← **다음**

### 2단계: 데이터 확장 (1-2주)
```bash
# 더 많은 법률 문서 수집
python data/collect/collect_labor_laws.py  # 데이터 증가
python data/process/index_labor_laws.py    # 재인덱싱

# GitHub 푸시 → 자동 재배포
git add . && git commit -m "Update: Expanded law data" && git push
```

### 3단계: 성능 최적화 (2-4주)
- 벡터DB 쿼리 최적화
- LLM 프롬프트 튜닝
- 캐싱 전략 추가

### 4단계: 모니터링 & 피드백 (지속)
- 사용자 피드백 수집
- API 로그 분석
- 모델 업그레이드 검토

---

## ⚠️ 주의사항

### 1. 하드웨어 요구사항
- **최소**: 16GB RAM (필수)
  - Qwen2.5-7B (4-bit): ~4GB
  - multilingual-e5-large: ~2GB
  - ChromaDB + OS: ~4-6GB
  - 버퍼: ~2GB

### 2. 첫 시작 시 모델 다운로드
- 첫 배포 후 **2-3분 추가 시간** 필요
- 모델 캐시 생성 후 다음 요청은 빠름
- 로그에서 `"Downloaded model"` 또는 유사 메시지 확인

### 3. 응답 시간
- 검색 + LLM 생성: **3-8초/질문**
- CPU 추론이므로 GPU보다 느림
- 필요시 GPU 하드웨어로 업그레이드 가능

### 4. 비용
- HF Spaces CPU (16GB): **무료** ✅
- 월 compute 시간: 무료

---

## 🆘 문제 해결 가이드

### 빌드 실패 (`Build failed`)

**Step 1**: Logs 탭 확인
```
Error: npm ERR! or pip ERR! 또는 Dockerfile 에러
```

**Step 2**: 로컬에서 재현 (Docker Desktop 필요)
```bash
cd /Users/chulheewon/development/proj/law
docker build -t law-chatbot:latest .
```

**Step 3**: 에러 해결 후 푸시
```bash
git add . && git commit -m "Fix: Build error" && git push
```

### 메모리 부족 (`Killed` 또는 `OOM`)

```
Java/Python 프로세스 갑자기 중단 → 메모리 부족
```

**해결**:
1. Space Settings → Hardware를 GPU-small 이상으로 변경
2. 또는 모델 크기 축소 (Qwen2.5-3B, 더 작은 임베딩 모델)

### 모델 다운로드 실패 (`HuggingFace timeout`)

**증상**: 처음 실행 후 60초 이상 "Loading..." 상태

**해결**:
1. 재시작 버튼 클릭 (Settings → Restart Space)
2. 2-3분 대기 (로그에서 모델 다운로드 진행 확인)

### API 응답 400 에러

**확인**: 요청 JSON 형식 검증
```json
✅ 올바른 형식:
{
  "message": "질문",
  "stream": false
}

❌ 틀린 형식:
{
  "query": "질문"  // "message"가 아님
}
```

---

## 📚 추가 리소스

- [HuggingFace Spaces 문서](https://huggingface.co/docs/hub/spaces)
- [Docker 배포 가이드](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [FastAPI 배포](https://fastapi.tiangolo.com/deployment/)
- [Next.js 배포](https://nextjs.org/docs/deployment)

---

## ✅ 체크리스트: HF Spaces 배포 전

- [ ] GitHub 리포지토리에 모든 코드 푸시 완료
- [ ] Dockerfile이 프로젝트 루트에 있음
- [ ] requirements.txt 모든 의존성 명시
- [ ] .dockerignore 파일 존재
- [ ] frontend/next.config.js에 `output: 'export'` 설정
- [ ] backend/requirements.txt에 fastapi, uvicorn 포함
- [ ] data/ 및 vectordb/ 디렉토리 존재
- [ ] HF Spaces Space 생성 (Docker, 16GB RAM)
- [ ] GitHub 리포지토리 연결 준비

---

## 🎯 최종 배포 상태

**준비도**: ✅ **100%**

**다음 액션**:
1. HuggingFace Spaces에서 새 Space 생성
2. GitHub 리포지토리 연결
3. 자동 배포 진행
4. 5-15분 후 `https://<USERNAME>-korean-law-chatbot.hf.space` 접속

---

*최종 업데이트: 2026년 1월 28일*
