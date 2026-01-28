from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    id: str
    content: str
    metadata: dict
    score: float = 0.0

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, http_request: Request):
    """
    법령/판례 검색 엔드포인트

    - query: 검색어
    - limit: 반환할 결과 수

    하이브리드 검색 (BM25 + 벡터)을 사용하여 관련 법령 및 판례를 검색합니다.
    """
    logger.info(f"Search request: {request.query}")

    try:
        # Access initialized components from app.state
        embeddings = getattr(http_request.app.state, "embeddings", None)
        retriever = getattr(http_request.app.state, "retriever", None)

        results = []

        if embeddings is not None and retriever is not None:
            # 1) 쿼리 임베딩
            try:
                q_emb = embeddings.encode(request.query)
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                raise HTTPException(status_code=500, detail=f"임베딩 생성 실패: {str(e)}")

            # 2) 하이브리드 검색
            try:
                search_results = retriever.hybrid_search(
                    query_embedding=q_emb,
                    query_text=request.query,
                    top_k=request.limit
                )

                logger.info(f"Found {len(search_results)} results")

                # 3) 결과 변환
                for idx, result in enumerate(search_results):
                    results.append(SearchResult(
                        id=result.get('id', f"result_{idx}"),
                        content=result.get('content', ''),
                        metadata=result.get('metadata', {}),
                        score=result.get('score', 0.0)
                    ))

            except Exception as e:
                logger.error(f"Retriever error: {e}")
                raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")
        else:
            logger.warning("Embeddings or Retriever not initialized")
            raise HTTPException(status_code=503, detail="검색 시스템이 초기화되지 않았습니다.")

        return SearchResponse(
            results=results,
            total_count=len(results)
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
