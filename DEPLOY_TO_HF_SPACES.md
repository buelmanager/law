# HuggingFace Spaces 배포 가이드

## 🚀 빠른 시작: GitHub 연동 배포

### 1단계: HuggingFace Space 설정

1. **HuggingFace Space 페이지 접속**
   - 🔗 https://huggingface.co/spaces/wonchulhee/korean-law-chatbot

2. **Settings 탭 클릭**

3. **Repository 섹션에서 "Connect to a Git repository" 클릭**

---

### 2단계: GitHub 리포지토리 연결

1. **Repository URL 입력**
   ```
   https://github.com/buelmanager/law
   ```

2. **Branch 선택**
   ```
   claude/slack-connection-setup-U2Dt9
   ```
   또는
   ```
   main
   ```
   (main 브랜치가 업데이트되면 main 사용 권장)

3. **"Connect" 버튼 클릭**

---

### 3단계: 자동 빌드 대기

HuggingFace가 자동으로:
1. GitHub 리포지토리 Clone
2. Dockerfile 감지 및 빌드
3. 컨테이너 실행 (포트 7860)
4. 헬스체크 (GET /api/health)

**예상 소요 시간**: 5-10분
- Docker 이미지 빌드: 3-5분
- Python 의존성 설치: 2-3분 (torch, transformers 등)
- 서버 시작: 30초

---

### 4단계: 배포 상태 확인

1. **Logs 탭에서 빌드 로그 확인**
   ```
   Building Docker image...
   Successfully built abc123
   Starting container...
   INFO:     Started server process [1]
   INFO:     Waiting for application startup.
   🚀 서버 시작
   ✅ 모든 모듈 초기화 완료 (가능한 항목)
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:7860
   ```

2. **오류 발생 시**
   - 빌드 로그에서 오류 메시지 확인
   - 주로 발생하는 문제:
     - Python 의존성 충돌
     - 메모리 부족 (16GB 초과)
     - 포트 7860 미사용

---

## 🔧 대체 방법: HuggingFace CLI로 배포

GitHub 연동이 작동하지 않을 경우:

### 1단계: HF CLI 설치

```bash
pip install -U huggingface_hub
```

### 2단계: 로그인

```bash
huggingface-cli login
# 토큰 입력: https://huggingface.co/settings/tokens
```

### 3단계: Space Clone

```bash
git clone https://huggingface.co/spaces/wonchulhee/korean-law-chatbot
cd korean-law-chatbot
```

### 4단계: 코드 복사

```bash
# 프로젝트 디렉토리로 이동
cd /home/user/law

# 모든 파일 복사 (vectordb 제외)
rsync -av --exclude='vectordb' --exclude='.git' --exclude='node_modules' \
    /home/user/law/ /path/to/korean-law-chatbot/
```

### 5단계: 커밋 및 푸시

```bash
cd /path/to/korean-law-chatbot
git add .
git commit -m "Deploy law chatbot with Slack integration"
git push
```

---

## ⚙️ 환경 변수 설정 (선택)

Slack 통합을 사용하려면 환경 변수를 설정해야 합니다.

### HuggingFace Spaces Settings에서 환경 변수 추가:

1. **Settings 탭 → Variables and secrets**

2. **다음 변수 추가:**

```bash
# Slack 통합 (선택)
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
ALLOWED_SLACK_USERS=U12345ABC,U67890DEF

# Claude CLI (선택)
CLAUDE_WORK_DIR=/app

# 모델 설정 (기본값 사용 가능)
EMBEDDINGS_MODEL_NAME=intfloat/multilingual-e5-large
CHROMADB_PATH=./vectordb
LLM_MODEL_PATH=./models/qwen2.5-7b-instruct-q4_k_m.gguf
```

3. **"Save" 클릭**

4. **Space 재시작** (Settings → Factory reboot)

---

## 🩺 헬스체크

배포 완료 후 다음 URL로 상태 확인:

```bash
curl https://wonchulhee-korean-law-chatbot.hf.space/api/health
```

**정상 응답:**
```json
{
  "status": "healthy",
  "service": "law-chatbot-api",
  "version": "0.1.0"
}
```

---

## 🔍 주요 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /` | 프론트엔드 UI (Next.js) |
| `POST /api/chat` | 법률 상담 채팅 |
| `POST /api/search` | 법령/판례 검색 |
| `POST /api/slack/events` | Slack 이벤트 수신 |
| `POST /api/slack/claude` | Claude CLI 원격 실행 |
| `GET /api/health` | 헬스체크 |

---

## ⚠️ 주의사항

### 1. vectordb 없음

현재 빌드에는 vectordb가 포함되지 않습니다.

**해결 방법:**

#### 옵션 A: 로컬에서 vectordb 생성 후 업로드
```bash
cd /home/user/law
python data/process/index_labor_laws.py
# vectordb/ 디렉토리 생성됨 (약 100MB)

# .gitignore에서 vectordb 임시 제거
sed -i '/^vectordb/d' .gitignore

# 커밋 및 푸시
git add vectordb/
git commit -m "Add pre-built vectordb"
git push
```

#### 옵션 B: Dockerfile에서 빌드 시 생성 (주석 해제)
```dockerfile
# Dockerfile:44-45 주석 제거
RUN python data/process/index_labor_laws.py
```

**주의**: 빌드 시간 +2-3분 소요

### 2. LLM 모델 다운로드

첫 실행 시 Qwen2.5-7B 모델 (~4GB)을 다운로드합니다.

**대응:**
- 첫 요청은 타임아웃 될 수 있음
- 2-3분 후 재시도
- 모델 다운로드 후에는 정상 속도 (3-8초)

### 3. 메모리 제한

HF Spaces 무료 티어: 16GB RAM

**대응:**
- 모델: 7B 이하 GGUF 4-bit 양자화
- 동시 요청 제한 (1-2개)
- 메모리 오류 시: Space 재시작

---

## 📊 배포 후 체크리스트

- [ ] Space 상태: "Running"
- [ ] Logs에서 오류 없음
- [ ] `/api/health` 응답 정상
- [ ] 프론트엔드 UI 로드 확인
- [ ] 채팅 테스트 (샘플 질문)
- [ ] (선택) Slack 통합 테스트
- [ ] (선택) vectordb 초기화 확인

---

## 🆘 문제 해결

### "Out of memory" 오류
- **원인**: 16GB RAM 초과
- **해결**: Space 재시작, 모델 크기 축소

### "Cannot find module 'vectordb'"
- **원인**: vectordb 디렉토리 없음
- **해결**: 옵션 A 또는 B 적용 (위 참조)

### "Model not found"
- **원인**: 모델 다운로드 실패
- **해결**: Logs 확인, 네트워크 문제 시 재시작

### "Port 7860 not accessible"
- **원인**: Dockerfile의 포트 설정 오류
- **해결**: Dockerfile 확인 (`EXPOSE 7860`, CMD에서 `--port 7860`)

### "Build failed"
- **원인**: 다양함 (의존성 충돌, Dockerfile 오류 등)
- **해결**: Logs에서 오류 메시지 확인, GitHub Issues에 보고

---

## 🔗 유용한 링크

- **HuggingFace Spaces 문서**: https://huggingface.co/docs/hub/spaces
- **Docker Spaces 가이드**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **프로젝트 GitHub**: https://github.com/buelmanager/law
- **Space URL**: https://wonchulhee-korean-law-chatbot.hf.space

---

## 🎉 배포 완료!

배포가 성공하면 다음 URL로 접속할 수 있습니다:

**🔗 https://wonchulhee-korean-law-chatbot.hf.space**

법률 질문을 입력하여 AI 상담을 받아보세요!
