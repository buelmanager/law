데이터 수집 안내

이 폴더에는 법령/판례 원문을 수집하는 스크립트가 포함됩니다.

사용법

1. 환경 변수 설정 (선택)

- `LAW_API_BASE_URL` (기본값: https://www.law.go.kr/api)
- `LAW_API_KEY` (필요한 경우)

2. 수집 실행

```bash
python data/collect/collect_labor_laws.py
```

설명

- `LawAPIClient`는 `data/collect/__init__.py`에 정의되어 있습니다. 현재 기본 구현은 플레이스홀더이며, 실제 API 스펙에 맞춰 `search_laws`와 `get_law_details`를 구현해야 합니다.
- 수집 결과는 `data/collect/labor_laws.jsonl`에 JSON Lines 형식으로 저장됩니다.
