# Slack에서 Claude Code CLI 원격 실행 가이드

이 가이드는 Slack에서 Claude Code CLI 명령을 실행하고, 모든 승인 요청을 자동으로 처리하는 방법을 설명합니다.

---

## 🎯 기능 개요

Slack에서 `/claude` 슬래시 커맨드를 사용하여 서버에서 Claude Code CLI를 원격으로 실행할 수 있습니다.

**주요 특징:**
- ✅ **자동 승인**: 모든 "허용하시겠습니까?" 질문에 자동으로 'y' 응답
- 🔒 **권한 제어**: 특정 Slack 사용자만 실행 가능
- 🛡️ **보안**: 위험한 명령(`rm -rf`, `sudo` 등) 자동 차단
- 📊 **실시간 피드백**: 실행 과정과 결과를 Slack으로 스트리밍

---

## 📋 사전 준비

### 1. Slack 앱 설정 완료

먼저 `SLACK_SETUP_GUIDE.md`를 따라 Slack 앱을 생성하고 설정해야 합니다.

### 2. 서버에 Claude CLI 설치

```bash
# Claude CLI 설치 (아직 설치 안 된 경우)
npm install -g @anthropics/claude

# 설치 확인
claude --version
```

### 3. 환경 변수 설정

`.env` 파일에 다음 변수 추가:

```bash
# 허용된 Slack 사용자 ID (쉼표로 구분)
ALLOWED_SLACK_USERS=U12345ABC,U67890DEF

# Claude CLI 작업 디렉토리
CLAUDE_WORK_DIR=/home/user/law
```

**Slack 사용자 ID 확인 방법:**
1. Slack에서 자신의 프로필 클릭
2. "..." 메뉴 → "Copy member ID"
3. 복사한 ID를 `.env`에 추가

---

## 🚀 Slack 슬래시 커맨드 설정

### 1단계: Slack App 설정

1. **Slack App 관리 페이지 접속**
   - 🔗 https://api.slack.com/apps
   - 생성한 앱 선택

2. **좌측 메뉴에서 "Slash Commands" 클릭**

3. **"Create New Command" 클릭**
   - **Command**: `/claude`
   - **Request URL**: `https://your-space.hf.space/api/slack/claude`
   - **Short Description**: `Claude Code CLI를 원격 실행합니다`
   - **Usage Hint**: `<명령>`

4. **"Save" 클릭**

5. **워크스페이스에 재설치**
   - "OAuth & Permissions" → "Reinstall App"

---

## 💡 사용 방법

### 기본 사용법

```
/claude <Claude Code 명령>
```

### 예시

#### 1. 파일 읽기
```
/claude 파일 읽기 backend/main.py
```

#### 2. 코드 검색
```
/claude 코드 검색 "Slack 연동"
```

#### 3. 함수 찾기
```
/claude 함수 찾기 process_question_and_respond
```

#### 4. 파일 수정
```
/claude backend/api/slack.py 파일의 타임아웃을 600초로 수정해줘
```

#### 5. Git 상태 확인
```
/claude git status 확인해줘
```

---

## 🔄 실행 흐름

### 1. 명령 전송
```
Slack: /claude 파일 읽기 backend/main.py
```

### 2. 즉시 응답 (3초 이내)
```
🤖 @user님의 Claude Code 명령을 실행합니다...
명령: `파일 읽기 backend/main.py`
```

### 3. 실행 시작
```
🤖 Claude Code 실행 중...
```
$ claude code "파일 읽기 backend/main.py"
```
```

### 4. 자동 승인 (필요 시)
```
✅ 자동 승인: Allow reading file? (y/n)
```

### 5. 결과 전송
```
✅ Claude Code 실행 완료 (exit code: 0)

```
[파일 내용...]
```
```

---

## 🛡️ 보안 기능

### 1. 권한 제어

**환경 변수로 허용된 사용자만 실행 가능**

```bash
# .env
ALLOWED_SLACK_USERS=U12345ABC,U67890DEF
```

권한이 없는 사용자가 시도하면:
```
❌ 권한이 없습니다. 관리자에게 문의하세요.
```

### 2. 위험한 명령 자동 차단

다음 명령은 자동으로 차단됩니다:

| 명령 | 이유 |
|------|------|
| `rm -rf`, `rm -r` | 파일 삭제 |
| `git push --force` | 강제 푸시 |
| `sudo` | 권한 상승 |
| `mkfs` | 파일시스템 포맷 |
| `dd if=` | 디스크 이미지 조작 |
| `> /dev/` | 시스템 디바이스 조작 |

차단 시 메시지:
```
❌ 보안상 위험한 명령은 실행할 수 없습니다.
```

### 3. 작업 디렉토리 제한

환경 변수로 지정한 디렉토리 내에서만 실행:
```bash
CLAUDE_WORK_DIR=/home/user/law
```

### 4. 타임아웃

명령 실행은 최대 5분(300초)까지만 허용됩니다.

---

## 🔍 상태 확인

### Claude CLI 연동 상태 확인

```bash
curl https://your-space.hf.space/api/claude/health
```

**응답 예시:**
```json
{
  "status": "active",
  "claude_installed": true,
  "work_dir": "/home/user/law",
  "allowed_users_configured": true,
  "allowed_users_count": 2
}
```

### 실행 중인 세션 확인

```bash
curl https://your-space.hf.space/api/claude/sessions
```

**응답 예시:**
```json
{
  "active_sessions": 1,
  "sessions": ["U12345ABC_1706428800.123"]
}
```

---

## 🐛 문제 해결

### 1. "claude: command not found"

**원인**: 서버에 Claude CLI가 설치되지 않음

**해결**:
```bash
npm install -g @anthropics/claude
```

### 2. "❌ 권한이 없습니다"

**원인**: 환경 변수에 사용자 ID가 없음

**해결**:
1. Slack에서 자신의 Member ID 복사
2. `.env`에 추가:
   ```bash
   ALLOWED_SLACK_USERS=U12345ABC
   ```
3. 서버 재시작

### 3. 명령이 실행되지 않음

**원인**: Request URL이 잘못되었거나 서버가 다운됨

**해결**:
1. Slack App 설정 → Slash Commands → Request URL 확인
2. 서버 상태 확인:
   ```bash
   curl https://your-space.hf.space/api/health
   ```

### 4. 타임아웃 발생

**원인**: 명령 실행이 5분 이상 소요

**해결**:
- `backend/api/claude_cli.py:79` → `timeout=300` 값 증가
- 또는 명령을 더 작은 단위로 분할

### 5. 출력이 잘림

**원인**: Slack 메시지 길이 제한 (3000자)

**해결**:
- `backend/api/claude_cli.py:98` → `max_output_length` 값 조정
- 또는 파일로 저장 후 링크 전송 (추가 구현 필요)

---

## ⚙️ 고급 설정

### 1. 타임아웃 변경

`backend/api/claude_cli.py:79`:
```python
child = pexpect.spawn(
    'claude',
    args=['code', command],
    cwd=WORK_DIR,
    encoding='utf-8',
    timeout=600  # 10분으로 변경
)
```

### 2. 출력 길이 제한 변경

`backend/api/claude_cli.py:98`:
```python
max_output_length = 5000  # 5000자로 변경
```

### 3. 자동 승인 패턴 추가

`backend/api/claude_cli.py:107-112`:
```python
index = child.expect([
    r'.*\(y/n\).*',
    r'.*\[y/n\].*',
    r'.*Allow\?.*',
    r'.*허용.*\?.*',
    r'.*승인.*\?.*',
    r'.*계속.*\?.*',  # 새 패턴 추가
    pexpect.EOF,
    pexpect.TIMEOUT
], timeout=2)
```

### 4. 위험한 명령 패턴 추가

`backend/api/claude_cli.py:44-54`:
```python
dangerous_patterns = [
    r'\brm\s+-rf\b',
    r'\brm\s+-r\b',
    r'\bgit\s+push\s+.*--force\b',
    r'\bsudo\b',
    r'\bmkfs\b',
    r'\bdd\s+if=',
    r'\b>\s*/dev/',
    r'\bchmod\s+777\b',  # 새 패턴 추가
]
```

---

## 📊 사용 예시

### 예시 1: 빠른 코드 검색

```
사용자: /claude "Slack 연동" 키워드로 코드 검색해줘

봇: 🤖 Claude Code 실행 중...

봇: ✅ Claude Code 실행 완료

backend/api/slack.py:
- 12: from slack_sdk import WebClient
- 85: # Slack 연동 API
...

frontend/docs/SLACK_SETUP_GUIDE.md:
- 1: # Slack 연동 설정 가이드
```

### 예시 2: 파일 수정

```
사용자: /claude backend/main.py 파일에서 포트를 8080으로 변경해줘

봇: 🤖 Claude Code 실행 중...

봇: ✅ 자동 승인: Modify backend/main.py? (y/n)

봇: ✅ Claude Code 실행 완료

backend/main.py 파일을 수정했습니다.
- 변경: port=7860 → port=8080
```

### 예시 3: Git 커밋

```
사용자: /claude 변경사항 커밋해줘

봇: 🤖 Claude Code 실행 중...

봇: ✅ 자동 승인: Stage all changes? (y/n)
봇: ✅ 자동 승인: Commit with message "Update port configuration"? (y/n)

봇: ✅ Claude Code 실행 완료

[main 1a2b3c4] Update port configuration
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

## 🔒 권장 보안 설정

### 프로덕션 환경

1. **허용 사용자 최소화**
   ```bash
   # 팀 리더나 관리자만
   ALLOWED_SLACK_USERS=U12345ABC
   ```

2. **작업 디렉토리 제한**
   ```bash
   # 특정 프로젝트 디렉토리만
   CLAUDE_WORK_DIR=/home/user/law
   ```

3. **위험한 명령 패턴 강화**
   - `git push`, `npm publish` 등 배포 명령 차단 고려
   - 프로덕션 브랜치 수정 차단

4. **감사 로그 추가**
   ```python
   # backend/api/claude_cli.py에 로깅 추가
   logger.info(f"User {user_id} executed: {command}")
   ```

---

## 📚 추가 리소스

- **Claude Code CLI 문서**: https://docs.anthropic.com/claude/docs/claude-code
- **pexpect 문서**: https://pexpect.readthedocs.io/
- **Slack Slash Commands**: https://api.slack.com/interactivity/slash-commands

---

## 🚦 다음 단계

이제 Slack에서 Claude Code를 원격으로 실행할 수 있습니다!

**시도해보기:**
```
/claude 안녕 Claude! 서버 상태 알려줘
```

**피드백**: GitHub Issues에 문제나 개선 사항을 제보해주세요.
