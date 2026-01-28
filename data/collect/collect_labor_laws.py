"""Collect labor law documents using a configurable law API client.

This script uses `LawAPIClient` from `data.collect` to query law names
and save results to `data/collect/labor_laws.jsonl`.

Usage:
    python data/collect/collect_labor_laws.py

Environment variables:
    LAW_API_BASE_URL - base URL for law API (defaults to https://www.law.go.kr/api)
    LAW_API_KEY - optional API key

Note: `LawAPIClient.search_laws` is a placeholder in this repo; adapt
its implementation to the target API (law.go.kr, 법제처 등).
"""

from pathlib import Path
import os
import logging
import sys

# Ensure project root is on sys.path so `import data` works when running script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.collect import save_documents, load_documents
from data.collect.law_go_kr import LawGoKRClient
from data.collect.supreme_court import SupremeCourtClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OUTPUT_PATH = Path(__file__).parent / "labor_laws.jsonl"

# 기본 수집 대상 법령 리스트 (노동법 중심)
LAW_NAMES = [
    "근로기준법",
    "근로자퇴직급여보장법",
    "남녀고용평등과 일·가정 양립 지원에 관한 법률",
    "최저임금법",
    "산업재해보상보험법",
]


def main():
    base_url = os.getenv("LAW_API_BASE_URL", LawGoKRClient.BASE_URL)
    api_key = os.getenv("LAW_API_KEY", None)

    client = LawGoKRClient(api_key=api_key)
    sc_client = SupremeCourtClient()

    all_docs = []
    for law_name in LAW_NAMES:
        logger.info(f"Searching law: {law_name}")
        try:
            # 법령 제목/목록 검색
            res = client.search_law_titles(keyword=law_name, page=1, per_page=100)
            docs = res if isinstance(res, list) else []

            # 가능한 경우 각 법령의 전문을 가져옴
            full_texts = []
            for item in docs:
                law_id = item.get("lawId") or item.get("id") or item.get("titlId")
                if law_id:
                    ft = client.get_law_fulltext(law_id)
                    if ft:
                        full_texts.append(ft)
            if full_texts:
                docs = full_texts

            # Fallback: 최소 메타데이터 저장
            if not docs:
                docs = [{
                    "id": law_name,
                    "law": law_name,
                    "content": "",
                    "source": base_url,
                }]

            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Error searching {law_name}: {e}")

    if all_docs:
        save_documents(all_docs, str(OUTPUT_PATH), format="jsonl")
        logger.info(f"Saved {len(all_docs)} documents to {OUTPUT_PATH}")
    else:
        logger.warning("No documents collected")


if __name__ == "__main__":
    main()
