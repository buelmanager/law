from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import logging
from typing import Optional, List
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)  # 입력 검증 추가
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[str] = []
    disclaimer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    법률 상담 채팅 엔드포인트

    - message: 사용자 질문
    - answer: AI 답변
    - sources: 참고 법령/판례
    - disclaimer: 면책 고지
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())
    logger.info(f"Chat request (id={conversation_id}): {request.message[:50]}...")

    try:
        # RAGService 사용
        from core.rag_service import RAGService

        rag_service = RAGService(
            embeddings_manager=getattr(http_request.app.state, "embeddings", None),
            retriever=getattr(http_request.app.state, "retriever", None),
            llm_manager=getattr(http_request.app.state, "llm", None),
        )

        # RAG 파이프라인 실행
        result = rag_service.process(
            question=request.message,
            top_k=5,
            max_tokens=512,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            answer=result.answer,
            sources=result.sources,
            disclaimer=result.disclaimer,
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")
