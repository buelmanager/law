# Slack 연동 설정 가이드

이 가이드는 AI 법률 상담 챗봇을 Slack 워크스페이스에 연결하는 방법을 설명합니다.

## 🎯 완료 후 가능한 기능

- **채팅방에서 @봇 멘션으로 법률 질문** → AI가 법령과 판례 기반 답변 제공
- **DM으로 개인 상담** → 1:1 법률 정보 상담
- **슬래시 커맨드** → `/법률상담 질문내용` 형태로 간편 호출

---

## 📋 사전 준비

1. **Slack 워크스페이스 관리자 권한** (앱 설치 권한 필요)
2. **서버 배포 완료** (HuggingFace Spaces 또는 자체 서버)
3. **공개 URL** (Slack이 접근 가능한 HTTPS URL)
   - 예: `https://your-space.hf.space` (HF Spaces)
   - 예: `https://your-domain.com` (자체 도메인)

---

## 🚀 단계별 설정

### 1단계: Slack 앱 생성

1. **Slack API 페이지 접속**
   - 🔗 https://api.slack.com/apps
   - 우측 상단 "Create New App" 클릭

2. **앱 생성 방식 선택**
   - **"From scratch"** 선택
   - **App Name**: `법률상담봇` (원하는 이름)
   - **Workspace**: 연결할 워크스페이스 선택
   - "Create App" 클릭

---

### 2단계: Bot Token 및 권한 설정

1. **좌측 메뉴에서 "OAuth & Permissions" 클릭**

2. **Bot Token Scopes 추가** (Scopes 섹션에서 아래 권한 추가)
   ```
   chat:write           # 메시지 전송
   app_mentions:read    # 멘션 수신
   im:history           # DM 읽기
   im:write             # DM 전송
   channels:history     # 채널 메시지 읽기
   groups:history       # 비공개 채널 메시지 읽기
   ```

3. **상단 "Install to Workspace" 클릭**
   - 권한 승인 화면에서 "Allow" 클릭

4. **Bot User OAuth Token 복사**
   - `xoxb-`로 시작하는 토큰
   - **🔒 안전하게 보관** (환경변수로 사용)

---

### 3단계: Event Subscriptions 설정 (앱 멘션/DM)

1. **좌측 메뉴에서 "Event Subscriptions" 클릭**

2. **Enable Events 토글 ON**

3. **Request URL 입력**
   ```
   https://your-space.hf.space/api/slack/events
   ```
   - ⚠️ 서버가 실행 중이어야 검증 성공
   - ✅ "Verified" 표시 확인

4. **Subscribe to bot events 섹션에서 이벤트 추가**
   ```
   app_mention      # @봇 멘션
   message.im       # DM 메시지
   ```

5. **하단 "Save Changes" 클릭**

---

### 4단계: Slash Commands 설정 (선택)

슬래시 커맨드(`/법률상담`)를 사용하려면 아래 단계를 진행하세요.

1. **좌측 메뉴에서 "Slash Commands" 클릭**

2. **"Create New Command" 클릭**
   - **Command**: `/법률상담`
   - **Request URL**: `https://your-space.hf.space/api/slack/command`
   - **Short Description**: `법률 질문을 AI에게 물어봅니다`
   - **Usage Hint**: `[질문 내용]`

3. **"Save" 클릭**

---

### 5단계: Signing Secret 확인

1. **좌측 메뉴에서 "Basic Information" 클릭**

2. **App Credentials 섹션에서 "Signing Secret" 복사**
   - 요청 검증용 (보안)

---

### 6단계: 환경 변수 설정

서버에 아래 환경 변수를 설정합니다.

#### HuggingFace Spaces인 경우

1. Space 설정 → "Settings" 탭 → "Repository secrets"
2. 아래 값 추가:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_SIGNING_SECRET=your-signing-secret-here
   ```

#### 로컬/자체 서버인 경우

`.env` 파일 생성:
```bash
# .env
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

**⚠️ `.env` 파일은 `.gitignore`에 추가하여 Git에 커밋하지 마세요!**

---

### 7단계: 워크스페이스에 봇 추가

1. **Slack 워크스페이스에서 봇을 채널에 초대**
   ```
   /invite @법률상담봇
   ```

2. **또는 채널 정보 → "Integrations" → "Add apps" → 봇 선택**

---

## ✅ 테스트

### 1) 앱 멘션 테스트
```
채팅방에서 입력:
@법률상담봇 부당해고 관련 질문이 있어요
```

**예상 응답:**
```
🤔 법령과 판례를 검색 중입니다...
(3~8초 후)
부당해고는 근로기준법 제23조에 따라...

📚 참고 법령: 근로기준법
⚠️ 본 서비스는 AI가 제공하는 일반적인 법률 정보이며...
```

### 2) DM 테스트
```
봇에게 DM 전송:
근로계약서 없이 일했는데 임금을 못 받았어요
```

### 3) 슬래시 커맨드 테스트
```
/법률상담 연차휴가 몇 일까지 쓸 수 있나요?
```

---

## 🔧 문제 해결

### "Endpoint not found" 오류
- **원인**: 서버가 실행 중이 아니거나 URL이 잘못됨
- **해결**:
  - HF Spaces: Space가 "Running" 상태인지 확인
  - 로컬: `uvicorn backend.main:app --host 0.0.0.0 --port 7860` 실행
  - URL 확인: `/api/slack/events` 경로가 정확한지 확인

### "URL verification failed"
- **원인**: 서버가 `url_verification` 이벤트를 처리하지 못함
- **해결**:
  - `backend/api/slack.py` 파일이 올바르게 배포되었는지 확인
  - 로그 확인: `{"type": "url_verification"}` 수신 여부

### 봇이 응답하지 않음
1. **환경 변수 확인**
   ```bash
   # 로그에서 아래 메시지 확인
   ✅ Slack 클라이언트 초기화 완료
   ```

2. **이벤트 구독 확인**
   - Slack App 설정 → Event Subscriptions → Subscribed Events에 `app_mention`, `message.im`이 있는지 확인

3. **봇이 채널에 있는지 확인**
   ```
   /invite @법률상담봇
   ```

### 3초 후 타임아웃
- **원인**: Slack은 3초 내에 응답을 요구하는데, LLM 추론이 더 오래 걸림
- **해결**: 이미 구현됨
  - `asyncio.create_task`로 백그라운드 처리
  - "생각 중..." 메시지 먼저 전송 → 완료 후 업데이트

---

## 📊 상태 확인 API

봇 상태를 확인하려면 아래 URL 접속:

```
GET https://your-space.hf.space/api/slack/health
```

**응답 예시:**
```json
{
  "status": "active",
  "bot_token_configured": true,
  "signing_secret_configured": true
}
```

---

## 🔐 보안 권장사항

1. **환경 변수로 토큰 관리**
   - ❌ 코드에 직접 하드코딩 금지
   - ✅ HF Spaces Secrets 또는 `.env` 파일 사용

2. **Signing Secret 검증**
   - 현재 코드는 검증을 건너뜀 (개발용)
   - 프로덕션에서는 반드시 구현:
     ```python
     from slack_sdk.signature import SignatureVerifier
     verifier = SignatureVerifier(SLACK_SIGNING_SECRET)
     verifier.is_valid_request(body, headers)
     ```

3. **HTTPS 필수**
   - Slack은 HTTPS만 지원
   - HF Spaces는 자동으로 HTTPS 제공

---

## 🎨 커스터마이징

### 1) 봇 이름 및 아이콘 변경
- Slack App 설정 → "Basic Information" → "Display Information"
- 아이콘, 이름, 설명 수정

### 2) 답변 포맷 변경
- `backend/api/slack.py` → `process_question_and_respond()` 함수
- `full_answer` 변수 수정
- Slack 마크다운 문법 사용 가능:
  ```
  *굵게*  _기울임_  `코드`  > 인용
  ```

### 3) 검색 결과 개수 조정
- `backend/api/slack.py:51` → `top_k=5` 수정

---

## 📚 추가 리소스

- **Slack API 공식 문서**: https://api.slack.com/docs
- **slack-sdk 문서**: https://slack.dev/python-slack-sdk/
- **Bolt 프레임워크** (더 고급 기능): https://slack.dev/bolt-python/

---

## 🐛 버그 리포트

Slack 연동 관련 문제가 있다면:
1. 서버 로그 확인: `backend/main.py` 실행 로그
2. Slack App 설정 → "Event Subscriptions" → Request Log 확인
3. GitHub Issues에 로그와 함께 제보

---

**🎉 설정 완료! 이제 Slack에서 법률 상담을 받아보세요!**
