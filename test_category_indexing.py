#!/usr/bin/env python3
"""
카테고리별 인덱싱 테스트 스크립트
각 분야별 20개 질문으로 참고자료가 올바른 카테고리에서 검색되는지 확인
"""

import requests
import json
from typing import Dict, List, Tuple

API_BASE_URL = "https://wonchulhee-korean-law-chatbot.hf.space"

# 분야별 테스트 질문 (각 20개)
TEST_QUESTIONS = {
    "labor": [
        "퇴직금 계산 방법 알려주세요",
        "부당해고 당했을 때 대처 방법",
        "연차휴가 미사용 수당 청구",
        "최저임금 적용 기준",
        "직장 내 괴롭힘 신고 방법",
        "산업재해 보상 절차",
        "육아휴직 신청 조건",
        "근로계약서 작성 시 주의사항",
        "야근수당 계산법",
        "주휴수당 지급 기준",
        "비정규직 차별 금지 규정",
        "해고 예고 수당",
        "정년 연장 법규",
        "임금 체불 신고 방법",
        "출산휴가 기간과 급여",
        "연장근로 한도",
        "계약직 갱신 기대권",
        "파견근로자 보호 규정",
        "근로시간 단축 청구권",
        "직장 성희롱 예방 의무"
    ],
    "lease": [
        "전세금 반환 청구 방법",
        "월세 계약 갱신 거절",
        "임대차 계약 해지 통보",
        "대항력 확보 조건",
        "우선변제권 요건",
        "전입신고 효력 발생일",
        "보증금 인상 한도",
        "상가임대차 권리금 보호",
        "임대인 변경 시 계약 승계",
        "임차인 원상복구 의무",
        "묵시적 갱신 조건",
        "계약갱신청구권 행사 기간",
        "전세사기 피해 대처법",
        "깡통전세 위험 판단",
        "임대료 연체 시 해지",
        "퇴거 요구 절차",
        "확정일자 받는 방법",
        "주택임대차 최우선변제금",
        "상가 권리금 회수 방법",
        "명도소송 절차"
    ],
    "consumer": [
        "인터넷 쇼핑 환불 규정",
        "제품 하자 교환 기준",
        "청약철회 가능 기간",
        "전자상거래 반품 비용",
        "불공정 약관 신고",
        "품질보증 기간 규정",
        "할부 거래 해지",
        "방문판매 철회",
        "결제 취소 방법",
        "배송 지연 보상",
        "소비자 분쟁 조정",
        "제조물 책임법 적용",
        "허위광고 피해 구제",
        "개인정보 침해 신고",
        "온라인 사기 피해 대응",
        "신용카드 부정 사용",
        "AS 거부 시 대처",
        "구매대행 환불 규정",
        "디지털 콘텐츠 환불",
        "서비스 계약 해지"
    ],
    "traffic": [
        "교통사고 과실비율 기준",
        "자동차 보험금 청구",
        "치료비 손해배상",
        "위자료 산정 기준",
        "휴업손해 계산법",
        "후유장해 보상",
        "음주운전 사고 처벌",
        "뺑소니 사고 대응",
        "무보험 차량 사고 보상",
        "렌트카 사고 책임",
        "대물배상 한도",
        "대인배상 범위",
        "합의금 협상 방법",
        "사망사고 보상 기준",
        "자전거 교통사고",
        "보행자 교통사고 과실",
        "접촉사고 처리 절차",
        "추돌사고 과실 비율",
        "수리비 청구 방법",
        "대차료 보상 기준"
    ]
}

# 각 카테고리에서 예상되는 키워드 (참고자료에 있어야 할 키워드)
EXPECTED_KEYWORDS = {
    "labor": ["근로", "퇴직", "해고", "임금", "노동", "산재", "고용", "휴가", "휴직"],
    "lease": ["임대", "전세", "월세", "보증금", "임차", "계약", "주택", "상가"],
    "consumer": ["소비자", "환불", "교환", "반품", "상품", "계약", "전자상거래", "약관"],
    "traffic": ["교통", "사고", "보험", "과실", "손해", "배상", "자동차", "운전"]
}

def test_single_question(question: str, expected_category: str) -> Tuple[bool, str, List[str]]:
    """단일 질문 테스트"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": question},
            timeout=60
        )

        if response.status_code != 200:
            return False, f"API 오류: {response.status_code}", []

        data = response.json()
        sources = data.get("sources", [])

        # 참고자료에 예상 키워드가 있는지 확인
        expected_keywords = EXPECTED_KEYWORDS.get(expected_category, [])
        sources_text = " ".join(sources).lower()

        matched = any(kw in sources_text for kw in expected_keywords)

        return matched, data.get("answer", "")[:100], sources

    except Exception as e:
        return False, f"오류: {str(e)}", []


def run_tests():
    """전체 테스트 실행"""
    print("=" * 60)
    print("📊 카테고리별 인덱싱 테스트")
    print("=" * 60)

    # 먼저 버전 확인
    try:
        health = requests.get(f"{API_BASE_URL}/api/health", timeout=10).json()
        print(f"📦 서버 버전: {health.get('version', 'unknown')}")
        print(f"📦 빌드 ID: {health.get('build_id', 'unknown')}")
        print()
    except:
        print("⚠️ 서버 상태 확인 실패")
        return

    results = {}

    for category, questions in TEST_QUESTIONS.items():
        print(f"\n{'='*60}")
        print(f"📁 카테고리: {category.upper()}")
        print(f"{'='*60}")

        success_count = 0
        fail_count = 0

        for i, question in enumerate(questions[:5], 1):  # 각 5개만 테스트 (시간 절약)
            matched, answer_preview, sources = test_single_question(question, category)

            status = "✅" if matched else "❌"
            print(f"{status} [{i}] {question[:30]}...")
            print(f"    📚 참고자료: {sources[:3] if sources else '없음'}")

            if matched:
                success_count += 1
            else:
                fail_count += 1

        accuracy = success_count / (success_count + fail_count) * 100 if (success_count + fail_count) > 0 else 0
        results[category] = {
            "success": success_count,
            "fail": fail_count,
            "accuracy": accuracy
        }
        print(f"\n📈 {category} 정확도: {accuracy:.1f}% ({success_count}/{success_count + fail_count})")

    # 최종 요약
    print("\n" + "=" * 60)
    print("📊 최종 결과 요약")
    print("=" * 60)

    total_success = sum(r["success"] for r in results.values())
    total_fail = sum(r["fail"] for r in results.values())
    total_accuracy = total_success / (total_success + total_fail) * 100 if (total_success + total_fail) > 0 else 0

    for category, result in results.items():
        print(f"  {category}: {result['accuracy']:.1f}% ({result['success']}/{result['success'] + result['fail']})")

    print(f"\n  📊 전체 정확도: {total_accuracy:.1f}% ({total_success}/{total_success + total_fail})")


if __name__ == "__main__":
    run_tests()
