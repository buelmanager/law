"""Client for fetching Supreme Court (대법원) decisions.

Note: The official 대법원 판례 DB may require credentials or use a separate
API. This module provides a small wrapper and falls back to scraping endpoints
if needed. Adjust `BASE_URL` and parsing for the actual target.
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SupremeCourtClient:
    # Placeholder public endpoint (adjust to actual API endpoint if available)
    BASE_URL = os.getenv("SUPREME_COURT_API_BASE", "https://www.scourt.go.kr/supreme/decisionSearch.do")

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()

    def search_cases(self, keyword: str, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """Search for cases containing keyword.

        This is a best-effort wrapper; for production use, adapt to the official
        API or use bulk dumps if available.
        """
        params = {
            "keyword": keyword,
            "page": page,
            "per_page": per_page,
        }
        try:
            resp = self.session.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            # For APIs returning JSON, parse; otherwise return empty list for now
            try:
                return resp.json()
            except Exception:
                return []
        except Exception as e:
            logger.error(f"search_cases error: {e}")
            return []

    def get_case(self, case_id: str) -> Dict[str, Any]:
        """Retrieve a specific case full text/metadata.

        Adjust parameter names depending on the endpoint.
        """
        try:
            resp = self.session.get(f"{self.BASE_URL}/{case_id}", timeout=30)
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"html": resp.text}
        except Exception as e:
            logger.error(f"get_case error: {e}")
            return {}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = SupremeCourtClient()
    print(client.search_cases("해고", page=1))
