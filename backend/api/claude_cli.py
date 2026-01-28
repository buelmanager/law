"""
Claude Code CLI 원격 실행 API

Slack에서 Claude Code 명령을 실행하고, 모든 승인을 자동으로 허용합니다.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import logging
import asyncio
import pexpect
import re
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Slack 클라이언트
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = None
if SLACK_BOT_TOKEN:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

# 허용된 사용자 ID (환경 변수로 설정)
ALLOWED_SLACK_USERS = os.getenv("ALLOWED_SLACK_USERS", "").split(",")
ALLOWED_SLACK_USERS = [u.strip() for u in ALLOWED_SLACK_USERS if u.strip()]

# 작업 디렉토리
WORK_DIR = os.getenv("CLAUDE_WORK_DIR", "/home/user/law")

# 실행 중인 세션 관리
active_sessions = {}


class ClaudeCommandRequest(BaseModel):
    """Claude Code 명령 요청"""
    command: str
    user_id: str
    channel_id: str
    thread_ts: Optional[str] = None


def is_dangerous_command(command: str) -> bool:
    """
    위험한 명령어 체크

    차단 목록:
    - rm -rf, rm -r (삭제)
    - git push --force (강제 푸시)
    - sudo (권한 상승)
    - mkfs (파일시스템 포맷)
    """
    dangerous_patterns = [
        r'\brm\s+-rf\b',
        r'\brm\s+-r\b',
        r'\bgit\s+push\s+.*--force\b',
        r'\bsudo\b',
        r'\bmkfs\b',
        r'\bdd\s+if=',
        r'\b>\s*/dev/',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


async def run_claude_code_with_auto_approve(
    command: str,
    channel: str,
    thread_ts: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Claude Code CLI를 실행하고 모든 승인을 자동으로 처리

    Args:
        command: 실행할 Claude Code 명령 (예: "파일 읽기 backend/main.py")
        channel: Slack 채널 ID
        thread_ts: 스레드 타임스탬프
        user_id: 사용자 ID
    """
    if not slack_client:
        logger.error("Slack 클라이언트가 초기화되지 않았습니다.")
        return

    session_id = f"{user_id}_{datetime.now().timestamp()}"
    active_sessions[session_id] = True

    try:
        # 시작 메시지
        start_msg = slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"🤖 Claude Code 실행 중...\n```\n$ claude code \"{command}\"\n```"
        )
        start_ts = start_msg["ts"]

        # Claude Code CLI 실행
        # pexpect를 사용하여 자동으로 'y' 응답
        child = pexpect.spawn(
            'claude',
            args=['code', command],
            cwd=WORK_DIR,
            encoding='utf-8',
            timeout=300  # 5분 타임아웃
        )

        output_buffer = []
        max_output_length = 3000  # Slack 메시지 길이 제한

        # 출력 수집 및 자동 승인
        while True:
            try:
                # 다양한 승인 요청 패턴 매칭
                index = child.expect([
                    r'.*\(y/n\).*',  # (y/n) 질문
                    r'.*\[y/n\].*',  # [y/n] 질문
                    r'.*Allow\?.*',  # Allow? 질문
                    r'.*허용.*\?.*',  # 한국어 허용 질문
                    r'.*승인.*\?.*',  # 한국어 승인 질문
                    pexpect.EOF,  # 프로세스 종료
                    pexpect.TIMEOUT  # 타임아웃
                ], timeout=2)

                # 출력 수집
                if child.before:
                    output_buffer.append(child.before)

                if index < 5:  # 승인 요청 감지
                    prompt_text = child.after if child.after else ""
                    logger.info(f"승인 요청 감지: {prompt_text}")

                    # Slack에 승인 알림 전송
                    slack_client.chat_postMessage(
                        channel=channel,
                        thread_ts=thread_ts,
                        text=f"✅ 자동 승인: {prompt_text.strip()}"
                    )

                    # 자동으로 'y' 입력
                    child.sendline('y')

                elif index == 5:  # EOF (정상 종료)
                    if child.before:
                        output_buffer.append(child.before)
                    break

                elif index == 6:  # TIMEOUT
                    # 타임아웃이지만 계속 읽기 시도
                    continue

            except pexpect.EOF:
                # 프로세스 종료
                break
            except pexpect.TIMEOUT:
                # 더 이상 출력이 없으면 종료
                if not child.isalive():
                    break
                continue

        # 프로세스 종료 대기
        child.close()
        exit_code = child.exitstatus

        # 출력 정리
        full_output = ''.join(output_buffer)
        full_output = full_output.strip()

        # 출력이 너무 길면 잘라내기
        if len(full_output) > max_output_length:
            full_output = full_output[:max_output_length] + "\n...(출력이 너무 길어 생략됨)"

        # 결과 전송
        result_emoji = "✅" if exit_code == 0 else "❌"
        result_text = f"{result_emoji} Claude Code 실행 완료 (exit code: {exit_code})\n\n```\n{full_output}\n```"

        # 시작 메시지 업데이트 또는 새 메시지 전송
        try:
            slack_client.chat_update(
                channel=channel,
                ts=start_ts,
                text=result_text
            )
        except:
            # 업데이트 실패 시 새 메시지 전송
            slack_client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=result_text
            )

        logger.info(f"✅ Claude Code 실행 완료 (exit: {exit_code})")

    except pexpect.ExceptionPexpect as e:
        logger.error(f"pexpect 오류: {e}")
        slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"❌ Claude Code 실행 오류: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Claude Code 실행 중 오류: {e}")
        slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"❌ 오류 발생: {str(e)}"
        )

    finally:
        # 세션 정리
        if session_id in active_sessions:
            del active_sessions[session_id]


@router.post("/slack/claude")
async def slack_claude_command(request: Request):
    """
    Slack 슬래시 커맨드: /claude <명령>

    예시:
    - /claude 파일 읽기 backend/main.py
    - /claude 코드 검색 "Slack 연동"
    - /claude 함수 찾기 process_question_and_respond

    설정:
    1. Slack App → Slash Commands
    2. Command: /claude
    3. Request URL: https://your-domain.com/api/slack/claude
    """
    from urllib.parse import parse_qs

    body = await request.body()
    params = parse_qs(body.decode('utf-8'))

    # 파라미터 추출
    text = params.get('text', [''])[0].strip()
    channel_id = params.get('channel_id', [''])[0]
    user_id = params.get('user_id', [''])[0]
    user_name = params.get('user_name', [''])[0]

    # 권한 체크
    if ALLOWED_SLACK_USERS and user_id not in ALLOWED_SLACK_USERS:
        logger.warning(f"권한 없는 사용자의 Claude 명령 시도: {user_id} ({user_name})")
        return {
            "response_type": "ephemeral",
            "text": "❌ 권한이 없습니다. 관리자에게 문의하세요."
        }

    # 명령어 검증
    if not text:
        return {
            "response_type": "ephemeral",
            "text": "사용법: `/claude <명령>`\n\n예시:\n- `/claude 파일 읽기 backend/main.py`\n- `/claude 코드 검색 \"Slack\"`"
        }

    # 위험한 명령 차단
    if is_dangerous_command(text):
        logger.warning(f"위험한 명령 차단: {text}")
        return {
            "response_type": "ephemeral",
            "text": "❌ 보안상 위험한 명령은 실행할 수 없습니다."
        }

    logger.info(f"📩 Claude 명령 수신: {text} (from {user_name})")

    # 비동기로 실행 (Slack 3초 제한 회피)
    asyncio.create_task(
        run_claude_code_with_auto_approve(
            command=text,
            channel=channel_id,
            user_id=user_id
        )
    )

    return {
        "response_type": "in_channel",
        "text": f"🤖 <@{user_id}>님의 Claude Code 명령을 실행합니다...\n명령: `{text}`"
    }


@router.get("/claude/sessions")
async def get_active_sessions():
    """현재 실행 중인 Claude Code 세션 조회"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }


@router.get("/claude/health")
async def claude_cli_health():
    """Claude CLI 연동 상태 확인"""
    import shutil

    claude_installed = shutil.which('claude') is not None

    return {
        "status": "active" if claude_installed else "claude_not_found",
        "claude_installed": claude_installed,
        "work_dir": WORK_DIR,
        "allowed_users_configured": len(ALLOWED_SLACK_USERS) > 0,
        "allowed_users_count": len(ALLOWED_SLACK_USERS),
    }
