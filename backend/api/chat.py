from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import logging
from typing import Optional, List
import uuid
import re

logger = logging.getLogger(__name__)

router = APIRouter()

# 분야별 카테고리 ID 매핑 (메타데이터 category 필드 필터링용)
# index_cases.py에서 인덱싱된 데이터의 category 필드와 매칭
CATEGORY_ID_MAP = {
    "노동법": "labor",
    "임대차법": "lease",
    "소비자보호법": "consumer",
    "교통사고": "traffic",
}

# 질문 내용 기반 카테고리 자동 감지용 키워드
CATEGORY_KEYWORDS = {
    "labor": [
        "퇴직금", "해고", "임금", "급여", "월급", "연봉", "연차", "휴가", "근로",
        "직장", "회사", "사용자", "근로자", "노동", "고용", "정규직", "비정규직",
        "계약직", "파견", "아르바이트", "알바", "최저임금", "야근", "연장근로",
        "휴일근로", "주휴", "퇴사", "사직", "해고예고", "부당해고", "직장내괴롭힘",
        "산재", "산업재해", "업무상재해", "출퇴근", "근로계약", "취업규칙",
        "육아휴직", "출산휴가", "남녀고용평등", "성희롱"
    ],
    "lease": [
        "전세", "월세", "보증금", "임대차", "임대인", "임차인", "집주인", "세입자",
        "계약갱신", "갱신청구", "대항력", "우선변제", "확정일자", "전입신고",
        "명도", "퇴거", "이사", "차임", "월차임", "상가임대", "상가", "점포",
        "권리금", "주택임대차", "임대료", "보증금반환", "전세사기", "깡통전세"
    ],
    "consumer": [
        "환불", "교환", "반품", "청약철회", "취소", "제품", "상품", "물건",
        "하자", "불량", "고장", "수리", "AS", "품질보증", "약관", "전자상거래",
        "온라인쇼핑", "인터넷쇼핑", "배송", "택배", "결제", "카드", "할부",
        "소비자", "판매자", "쇼핑몰", "구매", "주문", "배달"
    ],
    "traffic": [
        "교통사고", "자동차", "차량", "운전", "사고", "충돌", "접촉", "추돌",
        "과실", "과실비율", "보험", "자동차보험", "손해배상", "치료비", "위자료",
        "휴업손해", "후유장해", "장해", "사망", "음주운전", "뺑소니", "무보험",
        "대물", "대인", "합의금", "보험금", "렌트카", "대차료", "수리비"
    ]
}


def detect_category_from_question(question: str) -> Optional[str]:
    """
    질문 내용에서 키워드 기반으로 카테고리 자동 감지

    Returns:
        감지된 카테고리 ID (labor, lease, consumer, traffic) 또는 None
    """
    question_lower = question.lower()
    category_scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                category_scores[category] += 1

    # 가장 높은 점수의 카테고리 반환 (점수가 0이면 None)
    max_category = max(category_scores, key=category_scores.get)
    if category_scores[max_category] > 0:
        return max_category

    return None


def parse_category_from_message(message: str) -> tuple:
    """
    메시지에서 분야 정보를 파싱하고 실제 질문을 추출

    Returns:
        (category, clean_question) - 분야명과 정제된 질문
    """
    # "[노동법 관련 질문]" 형식 파싱
    pattern = r'\[(\S+)\s*관련\s*질문\]\s*(.+)'
    match = re.match(pattern, message, re.DOTALL)

    if match:
        category = match.group(1).strip()
        question = match.group(2).strip()
        return category, question

    return None, message


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
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

    - message: 사용자 질문 (분야 태그 포함 가능: "[노동법 관련 질문] 퇴직금은...")
    - answer: AI 답변
    - sources: 참고 법령/판례
    - disclaimer: 면책 고지
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # 분야 정보 파싱 (사용자가 선택한 분야)
    selected_category, clean_question = parse_category_from_message(request.message)
    logger.info(f"Chat request (id={conversation_id}, selected_category={selected_category}): {clean_question[:50]}...")

    # 1. 질문 내용 기반으로 카테고리 자동 감지
    detected_category = detect_category_from_question(clean_question)
    logger.info(f"Detected category from question: {detected_category}")

    # 2. 카테고리 결정: 감지된 카테고리 우선, 없으면 사용자 선택 사용
    category_filter = None
    if detected_category:
        category_filter = detected_category
        logger.info(f"Using detected category: {category_filter}")
    elif selected_category and selected_category in CATEGORY_ID_MAP:
        category_filter = CATEGORY_ID_MAP[selected_category]
        logger.info(f"Using selected category: {category_filter}")
    else:
        # 카테고리 미지정 시 전체 검색 (필터 없음)
        logger.info("No category filter applied, searching all categories")

    try:
        # RAGService 사용
        from backend.core.rag_service import RAGService

        rag_service = RAGService(
            embeddings_manager=getattr(http_request.app.state, "embeddings", None),
            retriever=getattr(http_request.app.state, "retriever", None),
            llm_manager=getattr(http_request.app.state, "llm", None),
        )

        # RAG 파이프라인 실행 (분야 필터링 포함)
        result = rag_service.process(
            question=clean_question,
            top_k=5,
            max_tokens=1024,
            category_filter=category_filter,
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
