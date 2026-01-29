from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import json
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# 법제처 법령 URL 매핑
LAW_URLS = {
    "근로기준법": "https://www.law.go.kr/법령/근로기준법",
    "근로자퇴직급여보장법": "https://www.law.go.kr/법령/근로자퇴직급여보장법",
    "남녀고용평등과 일·가정 양립 지원에 관한 법률": "https://www.law.go.kr/법령/남녀고용평등과일·가정양립지원에관한법률",
    "최저임금법": "https://www.law.go.kr/법령/최저임금법",
    "산업재해보상보험법": "https://www.law.go.kr/법령/산업재해보상보험법",
    "주택임대차보호법": "https://www.law.go.kr/법령/주택임대차보호법",
    "상가건물임대차보호법": "https://www.law.go.kr/법령/상가건물임대차보호법",
    "소비자기본법": "https://www.law.go.kr/법령/소비자기본법",
    "전자상거래등에서의소비자보호에관한법률": "https://www.law.go.kr/법령/전자상거래등에서의소비자보호에관한법률",
    "자동차손해배상보장법": "https://www.law.go.kr/법령/자동차손해배상보장법",
    "도로교통법": "https://www.law.go.kr/법령/도로교통법",
}


class LawInfo(BaseModel):
    id: str
    law: str
    article: str
    content: str
    source: str
    law_url: Optional[str] = None


class DownloadResponse(BaseModel):
    laws: List[LawInfo]
    total_count: int


@router.get("/download/laws", response_model=DownloadResponse)
async def get_all_laws():
    """
    인덱싱된 모든 법령 데이터 조회
    """
    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "collect" / "labor_laws.jsonl"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="법령 데이터 파일을 찾을 수 없습니다.")

        laws = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    law_name = data.get("law", "")
                    laws.append(LawInfo(
                        id=data.get("id", ""),
                        law=law_name,
                        article=data.get("article", ""),
                        content=data.get("content", ""),
                        source=data.get("source", ""),
                        law_url=LAW_URLS.get(law_name)
                    ))

        return DownloadResponse(
            laws=laws,
            total_count=len(laws)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching laws: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/laws/{law_id}")
async def get_law_by_id(law_id: str):
    """
    특정 법령 조문 조회
    """
    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "collect" / "labor_laws.jsonl"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="법령 데이터 파일을 찾을 수 없습니다.")

        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("id") == law_id:
                        law_name = data.get("law", "")
                        return LawInfo(
                            id=data.get("id", ""),
                            law=law_name,
                            article=data.get("article", ""),
                            content=data.get("content", ""),
                            source=data.get("source", ""),
                            law_url=LAW_URLS.get(law_name)
                        )

        raise HTTPException(status_code=404, detail=f"법령 '{law_id}'를 찾을 수 없습니다.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching law: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/laws.json")
async def download_laws_json():
    """
    모든 법령 데이터를 JSON 파일로 다운로드
    """
    try:
        data_path = Path(__file__).parent.parent.parent / "data" / "collect" / "labor_laws.jsonl"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="법령 데이터 파일을 찾을 수 없습니다.")

        laws = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    law_name = data.get("law", "")
                    laws.append({
                        "id": data.get("id", ""),
                        "law": law_name,
                        "article": data.get("article", ""),
                        "content": data.get("content", ""),
                        "source": data.get("source", ""),
                        "law_url": LAW_URLS.get(law_name)
                    })

        return JSONResponse(
            content={"laws": laws, "total_count": len(laws)},
            headers={
                "Content-Disposition": "attachment; filename=labor_laws.json"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading laws: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/law-urls")
async def get_law_urls():
    """
    법제처 법령 URL 목록 조회
    """
    return {
        "urls": LAW_URLS,
        "base_url": "https://www.law.go.kr"
    }
