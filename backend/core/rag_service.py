"""
RAG 서비스 - 공통 RAG 파이프라인
chat.py, slack.py, claude_cli.py에서 중복되던 로직을 통합
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RAGResult:
    """RAG 파이프라인 결과"""
    answer: str
    sources: List[str]
    context: str
    disclaimer: str


class RAGService:
    """
    RAG 파이프라인 서비스
    임베딩 → 검색 → 컨텍스트 구성 → LLM 추론을 통합 관리
    """

    def __init__(
        self,
        embeddings_manager=None,
        retriever=None,
        llm_manager=None,
    ):
        self.embeddings = embeddings_manager
        self.retriever = retriever
        self.llm = llm_manager

        # 프롬프트 로드
        try:
            from backend.core.prompts import SYSTEM_PROMPT_LABOR_LAW, RAG_PROMPT_TEMPLATE, DISCLAIMER
            self.system_prompt = SYSTEM_PROMPT_LABOR_LAW
            self.rag_template = RAG_PROMPT_TEMPLATE
            self.disclaimer = DISCLAIMER
        except ImportError:
            logger.warning("Failed to import prompts, using defaults")
            self.system_prompt = "당신은 한국 노동법 전문 AI 어시스턴트입니다."
            self.rag_template = "컨텍스트:\n{context}\n\n질문: {question}\n\n답변:"
            self.disclaimer = "본 서비스는 AI가 제공하는 일반적인 법률 정보이며, 정식 법률 자문이 아닙니다."

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 수행

        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수

        Returns:
            검색 결과 리스트 [{"content": ..., "metadata": {...}}, ...]
        """
        if self.embeddings is None or self.retriever is None:
            logger.warning("Embeddings or Retriever not initialized")
            return []

        try:
            # 쿼리 임베딩
            query_embedding = self.embeddings.encode(query)

            # 하이브리드 검색
            results = self.retriever.hybrid_search(
                query_embedding=query_embedding,
                query_text=query,
                top_k=top_k
            )
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        검색 결과로부터 컨텍스트 문자열 구성

        Args:
            search_results: 검색 결과 리스트

        Returns:
            포맷팅된 컨텍스트 문자열
        """
        if not search_results:
            return ""

        context_parts = []
        for r in search_results:
            law_name = r.get('metadata', {}).get('law', '알 수 없음')
            content = r.get('content', '')
            context_parts.append(f"[{law_name}] {content}")

        return "\n\n".join(context_parts)

    def extract_sources(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        검색 결과에서 출처 목록 추출

        Args:
            search_results: 검색 결과 리스트

        Returns:
            출처 문자열 리스트
        """
        sources = []
        for r in search_results:
            law_name = r.get('metadata', {}).get('law', '')
            if law_name and law_name not in sources:
                sources.append(law_name)
        return sources

    def generate_answer(
        self,
        question: str,
        context: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        LLM을 사용하여 답변 생성

        Args:
            question: 사용자 질문
            context: RAG 컨텍스트
            max_tokens: 최대 토큰 수
            temperature: 샘플링 온도

        Returns:
            생성된 답변 문자열
        """
        if self.llm is None:
            logger.warning("LLM not configured, returning context-based response")
            if context:
                return f"관련 법령 정보를 찾았습니다:\n\n{context[:1000]}...\n\n(참고: LLM이 구성되지 않아 상세 답변 생성이 불가합니다)"
            return "죄송합니다. 현재 AI 응답 생성 기능을 사용할 수 없습니다. 잠시 후 다시 시도해주세요."

        try:
            # 프롬프트 구성
            prompt = self.system_prompt + "\n\n" + self.rag_template.format(
                context=context if context else "관련 법령 정보가 없습니다.",
                question=question
            )
            logger.info(f"[RAG] Prompt length: {len(prompt)} chars")
            logger.info(f"[RAG] Starting LLM generation...")

            # LLM 추론
            import time
            start_time = time.time()
            answer = self.llm.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            elapsed = time.time() - start_time
            logger.info(f"[RAG] LLM generation completed in {elapsed:.2f}s, answer length: {len(answer)} chars")
            return answer
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            if context:
                return f"응답 생성 중 오류가 발생했습니다. 관련 법령 정보:\n\n{context[:500]}..."
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def process(
        self,
        question: str,
        top_k: int = 5,
        max_tokens: int = 512,
    ) -> RAGResult:
        """
        전체 RAG 파이프라인 실행

        Args:
            question: 사용자 질문
            top_k: 검색 결과 수
            max_tokens: LLM 최대 토큰

        Returns:
            RAGResult 객체
        """
        # 1. 검색
        search_results = self.search(question, top_k=top_k)

        # 2. 컨텍스트 구성
        context = self.build_context(search_results)

        # 3. 출처 추출
        sources = self.extract_sources(search_results)

        # 4. 답변 생성
        answer = self.generate_answer(question, context, max_tokens=max_tokens)

        return RAGResult(
            answer=answer,
            sources=sources,
            context=context,
            disclaimer=self.disclaimer,
        )
