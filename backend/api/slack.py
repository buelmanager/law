"""
Slack Bot 연동 API

Slack 워크스페이스에서 @봇 멘션으로 법률 질문을 받고 답변을 전송합니다.
"""
from fastapi import APIRouter, Request, HTTPException
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# Slack 클라이언트 초기화 (환경변수에서 토큰 로드)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

slack_client = None
if SLACK_BOT_TOKEN:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
    logger.info("✅ Slack 클라이언트 초기화 완료")
else:
    logger.warning("⚠️ SLACK_BOT_TOKEN이 설정되지 않았습니다. Slack 연동이 비활성화됩니다.")


def verify_slack_request(request: Request, body: bytes) -> bool:
    """
    Slack 요청 서명 검증 (보안)

    참고: https://api.slack.com/authentication/verifying-requests-from-slack
    """
    if not SLACK_SIGNING_SECRET:
        logger.warning("SLACK_SIGNING_SECRET이 없어 서명 검증을 건너뜁니다.")
        return True

    # 실제 프로덕션에서는 반드시 구현 필요
    # slack_sdk.signature.SignatureVerifier 사용 권장
    return True


async def process_question_and_respond(question: str, channel: str, thread_ts: Optional[str] = None, app_state=None):
    """
    법률 질문을 RAG로 처리하고 Slack 채널에 답변 전송

    Args:
        question: 사용자 질문
        channel: Slack 채널 ID
        thread_ts: 스레드 타임스탬프 (답글로 보낼 경우)
        app_state: FastAPI app.state (LLM, Retriever 등)
    """
    if not slack_client:
        logger.error("Slack 클라이언트가 초기화되지 않았습니다.")
        return

    try:
        # "생각 중..." 메시지 전송 (사용자 경험 개선)
        thinking_msg = slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="🤔 법령과 판례를 검색 중입니다..."
        )
        thinking_ts = thinking_msg["ts"]

        # RAG 파이프라인 실행
        embeddings = getattr(app_state, "embeddings", None)
        retriever = getattr(app_state, "retriever", None)
        llm = getattr(app_state, "llm", None)

        search_results = []
        if embeddings and retriever:
            # 1) 쿼리 임베딩
            q_emb = embeddings.encode(question)

            # 2) 하이브리드 검색
            try:
                search_results = retriever.hybrid_search(
                    query_embedding=q_emb,
                    query_text=question,
                    top_k=5
                )
                logger.info(f"검색 결과: {len(search_results)}개")
            except Exception as e:
                logger.error(f"Retriever 오류: {e}")

        # 3) 컨텍스트 구성
        context = "\n\n".join([
            f"[{r.get('metadata', {}).get('law', '')}] {r.get('content', '')}"
            for r in search_results
        ])

        # 4) 프롬프트 생성
        from core.prompts import SYSTEM_PROMPT_LABOR_LAW, RAG_PROMPT_TEMPLATE, DISCLAIMER
        prompt = SYSTEM_PROMPT_LABOR_LAW + "\n\n" + RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

        # 5) LLM 추론
        answer = "죄송합니다. LLM 모델이 로드되지 않았습니다."
        if llm:
            try:
                answer = llm.generate(prompt, max_tokens=512)
            except Exception as e:
                logger.error(f"LLM 생성 오류: {e}")
                answer = f"응답 생성 중 오류가 발생했습니다: {str(e)}"

        # 6) 출처 정리
        sources = []
        for r in search_results[:3]:  # 상위 3개만
            law_name = r.get('metadata', {}).get('law', '알 수 없음')
            if law_name not in sources:
                sources.append(law_name)

        sources_text = "\n📚 *참고 법령:* " + ", ".join(sources) if sources else ""

        # 7) 최종 답변 구성
        full_answer = f"{answer}\n\n{sources_text}\n\n⚠️ _{DISCLAIMER}_"

        # "생각 중..." 메시지 삭제
        slack_client.chat_delete(channel=channel, ts=thinking_ts)

        # 최종 답변 전송
        slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=full_answer,
            mrkdwn=True  # 마크다운 포맷 활성화
        )

        logger.info(f"✅ Slack 답변 전송 완료 (채널: {channel})")

    except SlackApiError as e:
        logger.error(f"Slack API 오류: {e.response['error']}")
    except Exception as e:
        logger.error(f"답변 처리 중 오류: {e}")
        # 오류 메시지 전송
        try:
            slack_client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=f"❌ 죄송합니다. 오류가 발생했습니다: {str(e)}"
            )
        except:
            pass


@router.post("/slack/events")
async def slack_events(request: Request):
    """
    Slack Events API 엔드포인트

    Slack 앱에서 발생하는 이벤트(멘션, DM 등)를 수신합니다.

    설정 필요:
    1. Slack App 생성 → https://api.slack.com/apps
    2. Event Subscriptions 활성화
    3. Request URL: https://your-domain.com/api/slack/events
    4. Subscribe to bot events: app_mention, message.im
    """
    body = await request.json()

    # Slack URL 검증 (최초 설정 시)
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    # 이벤트 처리
    if body.get("type") == "event_callback":
        event = body.get("event", {})
        event_type = event.get("type")

        # 봇 자신의 메시지는 무시
        if event.get("bot_id"):
            return {"ok": True}

        # 앱 멘션 처리
        if event_type == "app_mention":
            text = event.get("text", "")
            channel = event.get("channel")
            thread_ts = event.get("thread_ts") or event.get("ts")

            # 멘션 제거 (<@U12345> 형태)
            import re
            question = re.sub(r'<@[A-Z0-9]+>', '', text).strip()

            if not question:
                question = "안녕하세요! 법률 질문을 입력해주세요."

            logger.info(f"📩 Slack 질문 수신: {question[:50]}...")

            # 비동기로 답변 처리 (Slack 3초 제한 회피)
            import asyncio
            asyncio.create_task(
                process_question_and_respond(
                    question=question,
                    channel=channel,
                    thread_ts=thread_ts,
                    app_state=request.app.state
                )
            )

            return {"ok": True}

        # DM 처리
        elif event_type == "message" and event.get("channel_type") == "im":
            text = event.get("text", "")
            channel = event.get("channel")

            logger.info(f"📩 Slack DM 수신: {text[:50]}...")

            import asyncio
            asyncio.create_task(
                process_question_and_respond(
                    question=text,
                    channel=channel,
                    app_state=request.app.state
                )
            )

            return {"ok": True}

    return {"ok": True}


@router.get("/slack/health")
async def slack_health():
    """Slack 연동 상태 확인"""
    status = "active" if slack_client else "inactive"
    return {
        "status": status,
        "bot_token_configured": bool(SLACK_BOT_TOKEN),
        "signing_secret_configured": bool(SLACK_SIGNING_SECRET),
    }


@router.post("/slack/command")
async def slack_command(request: Request):
    """
    Slack 슬래시 커맨드 처리

    예: /법률상담 부당해고 관련 질문입니다

    설정 필요:
    1. Slack App → Slash Commands
    2. Command: /법률상담
    3. Request URL: https://your-domain.com/api/slack/command
    """
    from urllib.parse import parse_qs

    body = await request.body()
    params = parse_qs(body.decode('utf-8'))

    # 파라미터 추출
    text = params.get('text', [''])[0]
    channel_id = params.get('channel_id', [''])[0]
    user_id = params.get('user_id', [''])[0]
    response_url = params.get('response_url', [''])[0]

    if not text:
        return {
            "response_type": "ephemeral",
            "text": "사용법: /법률상담 <질문 내용>"
        }

    logger.info(f"📩 Slack 커맨드 수신: {text[:50]}...")

    # 즉시 응답 (3초 제한)
    import asyncio
    asyncio.create_task(
        process_question_and_respond(
            question=text,
            channel=channel_id,
            app_state=request.app.state
        )
    )

    return {
        "response_type": "in_channel",
        "text": f"🤔 '<@{user_id}>님의 질문을 처리 중입니다...\n질문: {text}"
    }
