from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging
from typing import Optional, List
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
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
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    logger.info(f"Chat request (id={conversation_id}): {request.message[:50]}...")
    
    try:
        # Access initialized components from app.state
        embeddings = getattr(http_request.app.state, "embeddings", None)
        retriever = getattr(http_request.app.state, "retriever", None)
        llm = getattr(http_request.app.state, "llm", None)

        search_results = []
        if embeddings is not None and retriever is not None:
            # 1) 쿼리 임베딩
            q_emb = embeddings.encode(request.message)

            # 2) 하이브리드 검색
            try:
                search_results = retriever.hybrid_search(query_embedding=q_emb, query_text=request.message, top_k=5)
            except Exception as e:
                logger.warning(f"Retriever error: {e}")

        # 3) 컨텍스트 구성
        context = "\n\n".join([
            f"[{r.get('metadata', {}).get('law','')}] {r.get('content','')}" for r in search_results
        ])

        # 4) 프롬프트 생성
        from core.prompts import SYSTEM_PROMPT_LABOR_LAW, RAG_PROMPT_TEMPLATE, DISCLAIMER
        prompt = SYSTEM_PROMPT_LABOR_LAW + "\n\n" + RAG_PROMPT_TEMPLATE.format(context=context, question=request.message)

        # 5) LLM 추론
        if llm is not None:
            try:
                answer = llm.generate(prompt, max_tokens=512)
            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                answer = "죄송합니다. 응답 생성 중 오류가 발생했습니다."
        else:
            answer = f"'{request.message}'에 대한 답변입니다. (LLM 미구성)"

        # 출처 목록
        sources = [r.get('metadata', {}).get('law','') for r in search_results]

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=sources,
            disclaimer=DISCLAIMER,
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
