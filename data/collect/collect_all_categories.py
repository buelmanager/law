"""
4개 분야 확장 가능한 법률 데이터 수집기
- 노동법 (Phase 1 - 현재 활성화)
- 임대차법 (Phase 5-1)
- 소비자보호법 (Phase 5-2)
- 교통사고·손해배상 (Phase 5-3)

사용법:
    python collect_all_categories.py --category labor --max-items 500
    python collect_all_categories.py --all-enabled
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.collect.law_drf_client import LawDRFClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ========== 카테고리 정의 ==========
CATEGORIES: Dict[str, Dict[str, Any]] = {
    "labor": {
        "name": "노동법",
        "keywords": [
            "근로", "퇴직금", "해고", "임금", "근로기준법",
            "연차", "휴가", "최저임금", "산업재해", "직장내괴롭힘",
            "근로계약", "정년", "비정규직", "파견근로", "노동조합"
        ],
        "enabled": True,  # Phase 1 - 현재 활성화
        "priority": 1
    },
    "lease": {
        "name": "임대차법",
        "keywords": [
            "임대차", "전세", "월세", "보증금", "임차인",
            "임대인", "주택임대차", "상가임대차", "계약갱신", "퇴거",
            "명도", "차임", "대항력", "우선변제", "갱신거절"
        ],
        "enabled": False,  # Phase 5-1
        "priority": 2
    },
    "consumer": {
        "name": "소비자보호법",
        "keywords": [
            "환불", "하자", "약관", "전자상거래", "소비자",
            "청약철회", "품질보증", "제조물책임", "할부거래",
            "통신판매", "방문판매", "표시광고", "개인정보"
        ],
        "enabled": False,  # Phase 5-2
        "priority": 3
    },
    "traffic": {
        "name": "교통사고·손해배상",
        "keywords": [
            "교통사고", "손해배상", "과실비율", "보험", "자동차",
            "치료비", "위자료", "휴업손해", "후유장해", "사망사고",
            "음주운전", "뺑소니", "무보험", "대물배상", "대인배상"
        ],
        "enabled": False,  # Phase 5-3
        "priority": 4
    }
}


class CategoryDataCollector:
    """카테고리별 법률 데이터 수집기"""

    def __init__(self, output_dir: str = None):
        self.client = LawDRFClient()
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "raw" / "categories"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def collect_category(
        self,
        category_id: str,
        max_items_per_keyword: int = 100,
        collect_details: bool = True,
        detail_limit: int = 50
    ) -> Dict[str, Any]:
        """
        특정 카테고리의 판례 및 해석례 수집

        Args:
            category_id: 카테고리 ID (labor, lease, consumer, traffic)
            max_items_per_keyword: 키워드당 최대 수집 건수
            collect_details: 상세 정보 수집 여부
            detail_limit: 상세 수집 건수 제한

        Returns:
            수집 결과 통계
        """
        if category_id not in CATEGORIES:
            raise ValueError(f"Unknown category: {category_id}")

        category = CATEGORIES[category_id]
        logger.info(f"\n{'='*60}")
        logger.info(f"📂 카테고리: {category['name']} ({category_id})")
        logger.info(f"🔑 키워드: {len(category['keywords'])}개")
        logger.info(f"{'='*60}")

        # 결과 저장용
        all_precedents = {}  # id → item (중복 제거)
        all_interpretations = {}  # id → item (중복 제거)

        for keyword in category["keywords"]:
            logger.info(f"\n🔍 키워드 검색: '{keyword}'")

            # 판례 검색
            try:
                prec_result = self.client.search_precedents(
                    query=keyword,
                    display=max_items_per_keyword
                )
                for item in prec_result.get("items", []):
                    item["category"] = category_id
                    item["keyword"] = keyword
                    all_precedents[item["id"]] = item
                logger.info(f"  📜 판례: {len(prec_result.get('items', []))}건 (총 {prec_result.get('total', 0)}건)")
            except Exception as e:
                logger.warning(f"  ⚠️ 판례 검색 실패: {e}")

            # 법령해석례 검색
            try:
                expc_result = self.client.search_interpretations(
                    query=keyword,
                    display=max_items_per_keyword
                )
                for item in expc_result.get("items", []):
                    item["category"] = category_id
                    item["keyword"] = keyword
                    all_interpretations[item["id"]] = item
                logger.info(f"  📋 해석례: {len(expc_result.get('items', []))}건 (총 {expc_result.get('total', 0)}건)")
            except Exception as e:
                logger.warning(f"  ⚠️ 해석례 검색 실패: {e}")

        # 중복 제거된 결과
        unique_precs = list(all_precedents.values())
        unique_expcs = list(all_interpretations.values())

        logger.info(f"\n📊 수집 완료 (중복 제거 후)")
        logger.info(f"  - 판례: {len(unique_precs)}건")
        logger.info(f"  - 해석례: {len(unique_expcs)}건")

        # 상세 정보 수집
        detailed_precs = []
        detailed_expcs = []

        if collect_details:
            logger.info(f"\n📥 상세 정보 수집 (최대 {detail_limit}건씩)")

            # 판례 상세
            for i, item in enumerate(unique_precs[:detail_limit]):
                try:
                    detail = self.client.get_precedent_detail(item["id"])
                    if detail:
                        detail["category"] = item.get("category")
                        detail["keyword"] = item.get("keyword")
                        detailed_precs.append(detail)
                        if (i + 1) % 10 == 0:
                            logger.info(f"  판례 상세: {i + 1}/{min(len(unique_precs), detail_limit)}")
                except Exception as e:
                    logger.warning(f"  판례 상세 조회 실패 ({item['id']}): {e}")

            # 해석례 상세
            for i, item in enumerate(unique_expcs[:detail_limit]):
                try:
                    detail = self.client.get_interpretation_detail(item["id"])
                    if detail:
                        detail["category"] = item.get("category")
                        detail["keyword"] = item.get("keyword")
                        detailed_expcs.append(detail)
                        if (i + 1) % 10 == 0:
                            logger.info(f"  해석례 상세: {i + 1}/{min(len(unique_expcs), detail_limit)}")
                except Exception as e:
                    logger.warning(f"  해석례 상세 조회 실패 ({item['id']}): {e}")

        # 파일 저장
        self._save_jsonl(
            f"{category_id}_precedents_{self.timestamp}.jsonl",
            detailed_precs if detailed_precs else unique_precs
        )
        self._save_jsonl(
            f"{category_id}_interpretations_{self.timestamp}.jsonl",
            detailed_expcs if detailed_expcs else unique_expcs
        )

        return {
            "category": category_id,
            "name": category["name"],
            "precedents": {
                "search_count": len(unique_precs),
                "detail_count": len(detailed_precs)
            },
            "interpretations": {
                "search_count": len(unique_expcs),
                "detail_count": len(detailed_expcs)
            }
        }

    def collect_all_enabled(
        self,
        max_items_per_keyword: int = 100,
        collect_details: bool = True,
        detail_limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        활성화된 모든 카테고리 수집

        Returns:
            각 카테고리별 수집 결과 리스트
        """
        results = []

        enabled_categories = [
            (cat_id, cat)
            for cat_id, cat in CATEGORIES.items()
            if cat["enabled"]
        ]

        logger.info(f"\n🚀 활성화된 카테고리: {len(enabled_categories)}개")
        for cat_id, cat in enabled_categories:
            logger.info(f"  - {cat['name']} ({cat_id})")

        for cat_id, _ in sorted(enabled_categories, key=lambda x: x[1]["priority"]):
            result = self.collect_category(
                category_id=cat_id,
                max_items_per_keyword=max_items_per_keyword,
                collect_details=collect_details,
                detail_limit=detail_limit
            )
            results.append(result)

        # 총계 출력
        total_precs = sum(r["precedents"]["detail_count"] or r["precedents"]["search_count"] for r in results)
        total_expcs = sum(r["interpretations"]["detail_count"] or r["interpretations"]["search_count"] for r in results)

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 전체 수집 완료")
        logger.info(f"  - 총 판례: {total_precs}건")
        logger.info(f"  - 총 해석례: {total_expcs}건")
        logger.info(f"{'='*60}")

        return results

    def _save_jsonl(self, filename: str, items: List[Dict]):
        """JSONL 파일로 저장"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.info(f"💾 저장: {filepath} ({len(items)}건)")


def main():
    parser = argparse.ArgumentParser(description="법률 데이터 카테고리별 수집기")
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORIES.keys()),
        help="수집할 카테고리 (labor, lease, consumer, traffic)"
    )
    parser.add_argument(
        "--all-enabled", "-a",
        action="store_true",
        help="활성화된 모든 카테고리 수집"
    )
    parser.add_argument(
        "--max-items", "-m",
        type=int,
        default=100,
        help="키워드당 최대 검색 건수 (기본: 100)"
    )
    parser.add_argument(
        "--detail-limit", "-d",
        type=int,
        default=100,
        help="상세 수집 건수 제한 (기본: 100)"
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="상세 정보 수집 생략"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="출력 디렉토리"
    )
    parser.add_argument(
        "--enable-category",
        type=str,
        help="특정 카테고리 임시 활성화 (쉼표 구분)"
    )

    args = parser.parse_args()

    # 임시 카테고리 활성화
    if args.enable_category:
        for cat_id in args.enable_category.split(","):
            cat_id = cat_id.strip()
            if cat_id in CATEGORIES:
                CATEGORIES[cat_id]["enabled"] = True
                logger.info(f"✅ 카테고리 활성화: {cat_id}")

    collector = CategoryDataCollector(output_dir=args.output)

    if args.all_enabled:
        results = collector.collect_all_enabled(
            max_items_per_keyword=args.max_items,
            collect_details=not args.no_details,
            detail_limit=args.detail_limit
        )
    elif args.category:
        result = collector.collect_category(
            category_id=args.category,
            max_items_per_keyword=args.max_items,
            collect_details=not args.no_details,
            detail_limit=args.detail_limit
        )
        results = [result]
    else:
        parser.print_help()
        sys.exit(1)

    # 결과 요약 JSON 저장
    summary_path = collector.output_dir / f"collection_summary_{collector.timestamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": collector.timestamp,
            "categories": results
        }, f, ensure_ascii=False, indent=2)
    logger.info(f"\n📋 수집 요약: {summary_path}")


if __name__ == "__main__":
    main()
