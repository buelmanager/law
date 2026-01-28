from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import List

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
async def search(request: SearchRequest):
    """
    법령/판례 검색 엔드포인트
    
    - query: 검색어
    - limit: 반환할 결과 수
    """
    try:
        # TODO: 하이브리드 검색 (BM25 + 벡터) 구현
        logger.info(f"Search request: {request.query}")
        results = []
        
        return SearchResponse(
            results=results,
            total_count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error in search endpoint: {e}")
