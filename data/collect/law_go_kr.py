"""Client for 국가법령정보센터 (law.go.kr) and related law APIs.

This module provides a small wrapper to query law texts and metadata.

NOTE: API paths and parameters may change; set `LAW_API_BASE_URL` and
`LAW_API_KEY` environment variables as needed.
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LawGoKRClient:
    BASE_URL = os.getenv("LAW_API_BASE_URL", "https://www.law.go.kr/DRF/lawService.do")

    def __init__(self, api_key: Optional[str] = None):
        """Initialize client.

        Args:
            api_key: Optional API key for law.go.kr (if required)
        """
        self.api_key = api_key or os.getenv("LAW_API_KEY")
        self.session = requests.Session()

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        req_params = {**params}
        if self.api_key:
            req_params["OC"] = self.api_key

        logger.debug(f"LawGoKR query params: {req_params}")
        resp = self.session.get(self.BASE_URL, params=req_params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def search_law_titles(self, keyword: str, page: int = 1, per_page: int = 100) -> List[Dict[str, Any]]:
        """Search laws by keyword (returns basic metadata list).

        This uses the `search` style endpoint available on law.go.kr DRF API.
        Adjust parameters if you have a different endpoint.
        """
        params = {
            "OC": self.api_key or "",
            "target": "LAW",
            "countPerPage": per_page,
            "pageIndex": page,
            "type": "XML",
            "searchKeyword": keyword,
        }

        try:
            data = self._get(params)
            # law.go.kr responses may vary; attempt to extract reasonable fields
            items = []
            if isinstance(data, dict):
                # Try common keys
                for key in ("law", "laws", "법령", "data"):
                    if key in data:
                        potential = data[key]
                        if isinstance(potential, list):
                            items = potential
                            break
                # Fallback: look for 'result' -> 'statute' etc.
                if not items:
                    for v in data.values():
                        if isinstance(v, list):
                            items = v
                            break
            return items
        except Exception as e:
            logger.error(f"search_law_titles error: {e}")
            return []

    def get_law_fulltext(self, law_id: str) -> Dict[str, Any]:
        """Retrieve full text and metadata for a specific law_id.

        The exact parameter name depends on the API (e.g., `OC`, `titlId`, `lawId`).
        Try common variants and return first successful response.
        """
        candidates = [
            {"OC": self.api_key or "", "target": "LAW", "type": "XML", "lawId": law_id},
            {"OC": self.api_key or "", "target": "LAW", "type": "XML", "titlId": law_id},
        ]
        for params in candidates:
            try:
                data = self._get(params)
                return data
            except Exception:
                continue
        logger.warning(f"Unable to fetch fulltext for law_id={law_id}")
        return {}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = LawGoKRClient()
    print(client.search_law_titles("근로기준법", page=1, per_page=10))
