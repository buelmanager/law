"""
법제처 국가법령정보 공동활용 API 클라이언트
law.go.kr/DRF API를 사용하여 판례, 법령해석례, 헌재결정례 등을 수집

API 문서: https://open.law.go.kr/LSO/openApi/guideList.do
"""

import os
import requests
import xml.etree.ElementTree as ET
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# API 설정
BASE_URL = "http://www.law.go.kr/DRF/lawSearch.do"
DETAIL_URL = "http://www.law.go.kr/DRF/lawService.do"
DEFAULT_OC = "sapphire_5"  # 공개 테스트 계정


@dataclass
class LawCase:
    """판례/해석례 데이터 클래스"""
    id: str
    title: str
    case_number: str
    date: str
    court: str
    case_type: str
    content: str = ""
    summary: str = ""
    source: str = ""


class LawDRFClient:
    """법제처 DRF API 클라이언트"""

    def __init__(self, oc: str = None):
        """
        Args:
            oc: 사용자 ID (Open API 인증용)
        """
        self.oc = oc or os.getenv("LAW_DRF_OC", DEFAULT_OC)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; LawChatbot/1.0)"
        })

    def _parse_xml(self, xml_text: str) -> ET.Element:
        """XML 파싱"""
        return ET.fromstring(xml_text)

    def _get(self, url: str, params: Dict[str, Any]) -> str:
        """API 요청"""
        params["OC"] = self.oc
        params["type"] = "XML"

        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise

    # ========== 판례 (prec) ==========
    def search_precedents(
        self,
        query: str,
        page: int = 1,
        display: int = 100,
        date_from: str = None,
        date_to: str = None
    ) -> Dict[str, Any]:
        """
        판례 검색

        Args:
            query: 검색어
            page: 페이지 번호
            display: 한 페이지당 결과 수 (최대 100)
            date_from: 시작일 (YYYYMMDD)
            date_to: 종료일 (YYYYMMDD)

        Returns:
            {"total": int, "items": List[Dict]}
        """
        params = {
            "target": "prec",
            "query": query,
            "display": display,
            "page": page,
        }

        if date_from and date_to:
            params["prncYd"] = f"{date_from}~{date_to}"

        xml_text = self._get(BASE_URL, params)
        root = self._parse_xml(xml_text)

        total = int(root.findtext("totalCnt", "0"))
        items = []

        for prec in root.findall("prec"):
            items.append({
                "id": prec.findtext("판례일련번호", ""),
                "title": prec.findtext("사건명", ""),
                "case_number": prec.findtext("사건번호", ""),
                "date": prec.findtext("선고일자", ""),
                "court": prec.findtext("법원명", ""),
                "case_type": prec.findtext("사건종류명", ""),
                "detail_link": prec.findtext("판례상세링크", ""),
            })

        return {"total": total, "items": items}

    def get_precedent_detail(self, prec_id: str) -> Dict[str, Any]:
        """
        판례 상세 조회

        Args:
            prec_id: 판례일련번호

        Returns:
            판례 상세 정보
        """
        params = {
            "target": "prec",
            "ID": prec_id,
        }

        xml_text = self._get(DETAIL_URL, params)
        root = self._parse_xml(xml_text)

        # API 응답이 PrecService 또는 판례정보 태그 사용
        # root가 PrecService인 경우 직접 사용
        if root.tag == "PrecService":
            prec = root
        else:
            prec = root.find("판례정보") or root.find("PrecService")
            if prec is None:
                return {}

        return {
            "id": prec.findtext("판례정보일련번호", "") or prec.findtext("판례일련번호", ""),
            "title": prec.findtext("사건명", ""),
            "case_number": prec.findtext("사건번호", ""),
            "date": prec.findtext("선고일자", ""),
            "court": prec.findtext("법원명", ""),
            "case_type": prec.findtext("사건종류명", ""),
            "judgment_type": prec.findtext("판결유형", ""),
            "summary": prec.findtext("판시사항", ""),
            "holding": prec.findtext("판결요지", ""),
            "reference": prec.findtext("참조조문", ""),
            "reference_cases": prec.findtext("참조판례", ""),
            "full_text": prec.findtext("판례내용", ""),
        }

    # ========== 법령해석례 (expc) ==========
    def search_interpretations(
        self,
        query: str,
        page: int = 1,
        display: int = 100
    ) -> Dict[str, Any]:
        """
        법령해석례 검색

        Args:
            query: 검색어
            page: 페이지 번호
            display: 한 페이지당 결과 수

        Returns:
            {"total": int, "items": List[Dict]}
        """
        params = {
            "target": "expc",
            "query": query,
            "display": display,
            "page": page,
        }

        xml_text = self._get(BASE_URL, params)
        root = self._parse_xml(xml_text)

        total = int(root.findtext("totalCnt", "0"))
        items = []

        for expc in root.findall("expc"):
            items.append({
                "id": expc.findtext("법령해석례일련번호", ""),
                "title": expc.findtext("안건명", ""),
                "case_number": expc.findtext("안건번호", ""),
                "date": expc.findtext("회신일자", ""),
                "requester": expc.findtext("질의기관명", ""),
                "responder": expc.findtext("회신기관명", ""),
                "detail_link": expc.findtext("법령해석례상세링크", ""),
            })

        return {"total": total, "items": items}

    def get_interpretation_detail(self, expc_id: str) -> Dict[str, Any]:
        """
        법령해석례 상세 조회

        Args:
            expc_id: 법령해석례일련번호

        Returns:
            법령해석례 상세 정보
        """
        params = {
            "target": "expc",
            "ID": expc_id,
        }

        xml_text = self._get(DETAIL_URL, params)
        root = self._parse_xml(xml_text)

        # API 응답이 ExpcService 또는 법령해석례 태그 사용
        if root.tag == "ExpcService":
            expc = root
        else:
            expc = root.find("법령해석례") or root.find("ExpcService")
            if expc is None:
                return {}

        return {
            "id": expc.findtext("법령해석례일련번호", ""),
            "title": expc.findtext("안건명", ""),
            "case_number": expc.findtext("안건번호", ""),
            "date": expc.findtext("해석일자", "") or expc.findtext("회신일자", ""),
            "requester": expc.findtext("질의기관명", ""),
            "responder": expc.findtext("해석기관명", "") or expc.findtext("회신기관명", ""),
            "question": expc.findtext("질의요지", ""),
            "answer": expc.findtext("회답", ""),
            "reason": expc.findtext("이유", ""),
            "reference_laws": expc.findtext("참조조문", ""),
        }

    # ========== 헌재결정례 (detc) ==========
    def search_constitutional_decisions(
        self,
        query: str,
        page: int = 1,
        display: int = 100
    ) -> Dict[str, Any]:
        """
        헌재결정례 검색

        Args:
            query: 검색어
            page: 페이지 번호
            display: 한 페이지당 결과 수

        Returns:
            {"total": int, "items": List[Dict]}
        """
        params = {
            "target": "detc",
            "query": query,
            "display": display,
            "page": page,
        }

        xml_text = self._get(BASE_URL, params)
        root = self._parse_xml(xml_text)

        total = int(root.findtext("totalCnt", "0"))
        items = []

        for detc in root.findall("detc"):
            items.append({
                "id": detc.findtext("헌재결정례일련번호", ""),
                "title": detc.findtext("사건명", ""),
                "case_number": detc.findtext("사건번호", ""),
                "date": detc.findtext("선고일", ""),
                "case_type": detc.findtext("사건종류명", ""),
                "decision_type": detc.findtext("결정유형", ""),
                "detail_link": detc.findtext("헌재결정례상세링크", ""),
            })

        return {"total": total, "items": items}

    def get_constitutional_detail(self, detc_id: str) -> Dict[str, Any]:
        """
        헌재결정례 상세 조회

        Args:
            detc_id: 헌재결정례일련번호

        Returns:
            헌재결정례 상세 정보
        """
        params = {
            "target": "detc",
            "ID": detc_id,
        }

        xml_text = self._get(DETAIL_URL, params)
        root = self._parse_xml(xml_text)

        detc = root.find("헌재결정례")
        if detc is None:
            return {}

        return {
            "id": detc.findtext("헌재결정례일련번호", ""),
            "title": detc.findtext("사건명", ""),
            "case_number": detc.findtext("사건번호", ""),
            "date": detc.findtext("선고일", ""),
            "case_type": detc.findtext("사건종류명", ""),
            "decision_type": detc.findtext("결정유형", ""),
            "holding": detc.findtext("결정요지", ""),
            "full_text": detc.findtext("결정문", ""),
            "reference_laws": detc.findtext("참조조문", ""),
        }

    # ========== 법령 전문 (law) ==========
    def get_law_detail(self, mst: str) -> Dict[str, Any]:
        """
        법령 전문 조회

        Args:
            mst: 법령일련번호

        Returns:
            법령 상세 정보
        """
        params = {
            "target": "law",
            "MST": mst,
        }

        xml_text = self._get(DETAIL_URL, params)
        root = self._parse_xml(xml_text)

        law = root.find("법령")
        if law is None:
            return {}

        # 조문 추출
        articles = []
        for jo in law.findall(".//조문"):
            articles.append({
                "number": jo.findtext("조문번호", ""),
                "title": jo.findtext("조문제목", ""),
                "content": jo.findtext("조문내용", ""),
            })

        return {
            "id": law.findtext("법령ID", ""),
            "mst": mst,
            "name": law.findtext("법령명_한글", ""),
            "type": law.findtext("법령구분명", ""),
            "ministry": law.findtext("소관부처명", ""),
            "proclamation_date": law.findtext("공포일자", ""),
            "enforcement_date": law.findtext("시행일자", ""),
            "articles": articles,
        }

    # ========== 대량 수집 유틸리티 ==========
    def collect_all(
        self,
        target: str,
        query: str,
        max_items: int = None,
        delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        전체 데이터 수집 (페이지네이션 처리)

        Args:
            target: "prec" | "expc" | "detc"
            query: 검색어
            max_items: 최대 수집 개수 (None이면 전체)
            delay: 요청 간 딜레이 (초)

        Returns:
            수집된 아이템 리스트
        """
        search_func = {
            "prec": self.search_precedents,
            "expc": self.search_interpretations,
            "detc": self.search_constitutional_decisions,
        }.get(target)

        if not search_func:
            raise ValueError(f"Unknown target: {target}")

        all_items = []
        page = 1
        display = 100

        while True:
            logger.info(f"Fetching {target} page {page}...")
            result = search_func(query=query, page=page, display=display)

            items = result.get("items", [])
            if not items:
                break

            all_items.extend(items)

            if max_items and len(all_items) >= max_items:
                all_items = all_items[:max_items]
                break

            total = result.get("total", 0)
            if len(all_items) >= total:
                break

            page += 1
            time.sleep(delay)

        logger.info(f"Collected {len(all_items)} {target} items")
        return all_items


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = LawDRFClient()

    # 판례 검색 테스트
    print("\n=== 판례 검색 (근로) ===")
    result = client.search_precedents("근로", display=3)
    print(f"Total: {result['total']}")
    for item in result["items"]:
        print(f"  - [{item['case_number']}] {item['title'][:50]}...")

    # 법령해석례 검색 테스트
    print("\n=== 법령해석례 검색 (근로) ===")
    result = client.search_interpretations("근로", display=3)
    print(f"Total: {result['total']}")
    for item in result["items"]:
        print(f"  - [{item['case_number']}] {item['title'][:50]}...")

    # 헌재결정례 검색 테스트
    print("\n=== 헌재결정례 검색 (근로) ===")
    result = client.search_constitutional_decisions("근로", display=3)
    print(f"Total: {result['total']}")
    for item in result["items"]:
        print(f"  - [{item['case_number']}] {item['title'][:50]}...")
