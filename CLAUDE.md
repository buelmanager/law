# 프로젝트: 무료 클라우드 기반 오픈소스 AI 법률 상담 챗봇

## 프로젝트 개요

무료 클라우드 서버 환경에서 특정 법률 분야에 특화된 오픈소스 AI 법률 상담 챗봇을 구축하는 프로젝트.
사용자가 법률 질문을 입력하면, 관련 법령과 판례를 검색(RAG)하여 근거 기반 답변을 생성한다.

> **핵심 원칙**: 이 서비스는 "법률 정보 제공"이지 "법률 자문"이 아니다. 변호사법 위반 리스크를 피하기 위해 모든 답변에 면책 고지를 포함하고, 개별 사안에 대한 단정적 결론을 제시하지 않는다.

---

## 아키텍처

```
사용자 질문
    → 임베딩 (multilingual-e5-large 또는 ko-sroberta)
    → 벡터DB 검색 (ChromaDB)
    → 관련 법령/판례 청크 추출
    → LLM 컨텍스트로 전달 (Qwen2.5-7B-Instruct, GGUF 4-bit)
    → 답변 생성 + 출처 명시
    → 면책 고지 첨부
```

### RAG (Retrieval-Augmented Generation) 우선 전략

- 파인튜닝보다 RAG를 우선 적용한다.
- 이유: 법령은 개정되므로 DB 업데이트만으로 최신 정보 반영 가능, 출처 명시 가능, 할루시네이션 감소.
- 파인튜닝(QLoRA)은 RAG만으로 성능이 부족할 때 Phase 3에서 추가 적용.

---

## 기술 스택 (확정)

### 서버 인프라
- **배포 플랫폼**: HuggingFace Spaces (Docker Space, 무료)
  - 16GB RAM, 2vCPU, 50GB 스토리지
  - 포트 7860 필수 (FastAPI에서 서빙)
  - 항시 가동, 무료

### AI 모델
- **LLM**: Qwen2.5-7B-Instruct (GGUF 4-bit 양자화)
  - 한국어 성능 우수, Apache 2.0 라이선스
  - llama-cpp-python으로 CPU 추론
- **임베딩**: intfloat/multilingual-e5-large (다국어+한국어)
- **벡터DB**: ChromaDB (경량, 메타데이터 필터링)
- **검색**: BM25 + 벡터 하이브리드 검색

### 프론트엔드
- **Next.js** (React 기반, 정적 빌드 후 FastAPI에서 서빙)
  - 채팅 UI, 법령 조문 하이라이트, 반응형 디자인

### 백엔드
- **FastAPI** (Python)
  - LLM 추론 API, RAG 검색 API
  - Next.js 정적 파일 서빙 (빌드 결과물)
  - 포트 7860에서 통합 서빙

### 배포 구조 (HuggingFace Spaces Docker)
```
Docker Container (HF Spaces, 포트 7860)
├── FastAPI 서버
│   ├── /api/chat          → LLM 추론 + RAG
│   ├── /api/search        → 법령/판례 검색
│   ├── /api/health        → 헬스체크
│   └── /* (static)        → Next.js 빌드 결과물 서빙
├── llama-cpp-python       → Qwen2.5-7B GGUF 로드
├── ChromaDB               → 벡터 저장소
└── Next.js (빌드 산출물)  → /app/frontend/out/
```

### 파인튜닝 (Phase 3)
- QLoRA (unsloth + peft), Google Colab T4에서 실행

---

## 데이터 소스

### 법령 데이터
- **국가법령정보센터** (law.go.kr): Open API 제공, 공공데이터로 자유 활용 가능
- **법제처 Open API**: 법령, 조문, 판례 검색 API 무료 제공

### 법제처 국가법령정보 공유서비스 API (승인됨)

| 항목 | 내용 |
|------|------|
| **End Point** | `https://apis.data.go.kr/1170000/law` |
| **데이터포맷** | XML |
| **활용기간** | 2026-01-29 ~ 2028-01-29 |
| **일일 트래픽** | 각 API 10,000건 |
| **라이선스** | 저작자표시 |

**API 엔드포인트 목록:**

| API | 경로 | 설명 |
|-----|------|------|
| 법령정보 | `/lawSearchList.do` | 현행법령 목록 조회 |
| 행정규칙 | `/admrulSearchList.do` | 행정규칙 목록 조회 |
| 자치법규 | `/ordinSearchList.do` | 자치법규 목록 조회 |
| 법령해석례 | `/expcSearchList.do` | 법령해석례 목록 조회 |
| 헌재결정례 | `/detcSearchList.do` | 헌재결정례 목록 조회 |
| 별표서식 | `/licbylSearchList.do` | 별표서식 목록 조회 |
| 법령용어 | `/lstrmSearchList.do` | 법령용어 목록 조회 |
| 조약정보 | `/trtySearchList.do` | 조약 목록 조회 |

> **인증키**: 환경변수 `LAW_API_KEY`에 설정 필요 (Encoding된 키 사용)

### 판례 데이터
- **대법원 공개 판례**: 공공저작물로 저작권 없음
- 판시사항, 판결요지, 이유 단위로 청킹

### 추가 데이터
- **AI Hub**: 법률 관련 한국어 데이터셋
- 법률 용어 사전 (동의어 확장용)
- 법률 Q&A 데이터셋 (파인튜닝 시 사용)

### 데이터 전처리 방식
1. API로 법령/판례 JSON 수집
2. 조문 단위 청킹 (법령: 조문별, 판례: 판시사항/이유별)
3. 메타데이터 태깅 (법령명, 조번호, 시행일, 판례번호)
4. 임베딩 생성 → ChromaDB 저장

---

## 특화 분야

### Phase 1 (현재): 노동법
- 부당해고, 임금체불, 근로계약, 직장 내 괴롭힘, 퇴직금, 연차휴가 등
- 주요 법령: 근로기준법, 근로자퇴직급여보장법, 남녀고용평등법, 최저임금법, 산업재해보상보험법
- 데이터 수집 범위: 노동 관련 법령 전문 + 대법원 노동 판례

### 확장 계획 (Phase 5 이후 순차 적용)
1. **임대차법** — 전월세 분쟁, 보증금 반환, 주택임대차보호법, 상가건물임대차보호법
2. **소비자보호법** — 환불, 하자, 약관, 전자상거래법, 소비자기본법
3. **교통사고·손해배상** — 과실비율, 보험, 손해배상 산정, 자동차손해배상보장법

> 각 분야 확장 시 해당 법령 데이터 수집 + 벡터DB 컬렉션 추가 + 프롬프트 분야별 분기 처리 필요.

---

## 인프라 제약사항

| 항목 | 제약 | 대응 |
|------|------|------|
| GPU 부재 (HF Spaces 무료) | 응답 10~30초 | 4-bit 양자화, 로딩 표시 UI |
| RAM 16GB | 대규모 모델 불가 | 7B 이하 GGUF 포맷 |
| 스토리지 50GB | 벡터DB 크기 제한 | 특정 분야 1개로 한정 |
| Colab 세션 제한 | 90분 유휴 시 종료 | 개발/파인튜닝 전용, 배포는 HF Spaces |

---

## 개발 로드맵 & 진행 현황

### Phase 1: 기본 RAG 챗봇 ✅ **완료**
- [x] 특화 분야 선택 → **노동법**
- [x] 기술 스택 확정 → HF Spaces + FastAPI + Next.js + llama-cpp
- [x] 프로젝트 스캐폴딩 (backend/, frontend/, Dockerfile)
- [x] 법제처/law.go.kr API로 노동법 법령 데이터 수집
  - 근로기준법, 근로자퇴직급여보장법, 남녀고용평등법, 최저임금법, 산업재해보상보험법 (5개)
  - 샘플 데이터: `data/collect/labor_laws.jsonl` (5 documents)
- [x] 텍스트 청킹 + 임베딩 생성
  - DocumentChunker: 조문 단위 + 텍스트 크기 기반 청킹
  - multilingual-e5-large: 1024 dim 임베딩
- [x] ChromaDB 벡터 저장소 구축
  - `./vectordb/` 디렉토리 (5 documents indexed, 영구 저장)
- [x] FastAPI 백엔드 (LLM 추론 + RAG 검색 API)
  - `POST /api/chat` - 채팅 (JSON 응답)
  - `POST /api/search` - 법령 검색 (하이브리드 검색)
  - `GET /api/health` - 헬스체크 (모듈 상태 포함)
- [x] Next.js 프론트엔드 (채팅 UI + 면책 고지)
  - ChatWindow.tsx, MessageBubble.tsx, Disclaimer.tsx
  - TypeScript + Tailwind CSS
- [x] Dockerfile 작성 (멀티스테이지 빌드)
  - Node.js 20 → Next.js 빌드
  - Python 3.11 → FastAPI 런타임
  - git 설치 (모델 다운로드용)
  - data/ + vectordb/ 포함
- [x] GitHub 커밋 및 푸시
  - Commit: `✨ Deploy: RAG-based Korean law chatbot ready for HF Spaces`
  - 38 files, 2402 insertions
- 🟡 HuggingFace Spaces 배포 (진행 중)
  - Space 생성: `korean-law-chatbot` (Docker, CPU 16GB)
  - GitHub 연결: `buelmanager/law` 리포지토리

### Phase 2: 판례 검색 추가
- [ ] 대법원 판례 데이터 수집 및 인덱싱
- [ ] 판례 요약 기능 (LLM 활용)
- [x] 하이브리드 검색 (BM25 + 벡터) - 이미 core/retriever.py에 구현
- [ ] 리랭킹 모델 추가

### Phase 3: 파인튜닝 (선택)
- [ ] 법률 Q&A 데이터셋 구축
- [ ] QLoRA 파인튜닝 (Colab T4)
- [ ] 평가 및 기존 RAG 대비 비교

### Phase 4: UI/UX 개선 및 안정화
- [ ] 대화 히스토리 (세션 내)
- [ ] 법령 조문 하이라이트 및 링크
- [ ] 사용자 피드백 수집
- [ ] 성능 모니터링

---

## 법적·윤리적 가이드라인

### 면책 고지 (모든 답변에 포함)
```
본 서비스는 AI가 제공하는 일반적인 법률 정보이며, 정식 법률 자문이 아닙니다.
구체적인 사안은 반드시 변호사와 상담하세요.
```

### 금지 사항
- 개별 사안에 대한 단정적 결론 제시 ("소송하세요", "이기실 수 있습니다" 등)
- 사용자 개인정보(이름, 주민번호 등) 수집 또는 저장
- 대화 내용 영구 저장 (세션 종료 시 삭제)

### 답변 작성 원칙
- 관련 법령 조문 번호를 반드시 인용
- 판례 인용 시 판례번호 명시
- 불확실한 내용은 "~할 수 있습니다", "~가능성이 있습니다"로 표현
- 복잡한 사안은 변호사 상담 권유

---

## 프로젝트 디렉토리 구조 (확정)

```
law/
├── CLAUDE.md                  # 프로젝트 컨텍스트 (이 파일)
├── Dockerfile                 # HF Spaces Docker 빌드
├── .env.example               # 환경 변수 템플릿
├── backend/
│   ├── main.py                # FastAPI 진입점 (포트 7860)
│   ├── api/
│   │   ├── chat.py            # /api/chat 엔드포인트
│   │   └── search.py          # /api/search 엔드포인트
│   ├── core/
│   │   ├── llm.py             # llama-cpp-python LLM 추론
│   │   ├── retriever.py       # RAG 검색 (ChromaDB + BM25)
│   │   ├── embeddings.py      # 임베딩 생성
│   │   ├── rag_service.py     # 공통 RAG 파이프라인 서비스
│   │   └── prompts.py         # 시스템 프롬프트 및 템플릿
│   └── requirements.txt       # Python 의존성
├── frontend/
│   ├── package.json
│   ├── next.config.js         # 정적 빌드 설정 (output: 'export')
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx       # 메인 채팅 페이지
│   │   └── components/
│   │       ├── ChatWindow.tsx  # 채팅 UI
│   │       ├── MessageBubble.tsx
│   │       └── Disclaimer.tsx  # 면책 고지 컴포넌트
│   └── public/
├── data/
│   ├── collect/               # 데이터 수집 스크립트
│   │   ├── law_go_kr.py       # 법제처 API 클라이언트
│   │   ├── supreme_court.py   # 대법원 판례 클라이언트
│   │   └── collect_labor_laws.py  # 노동법 수집 스크립트
│   ├── process/               # 전처리 스크립트
│   │   └── index_labor_laws.py    # 인덱싱 파이프라인
│   └── raw/                   # 원본 데이터
├── vectordb/                  # ChromaDB 저장소 (빌드 시 생성 또는 포함)
└── models/                    # GGUF 모델 (빌드 시 다운로드)
```

---

## 작업 시 참고사항

### 백엔드 (Python)
- Python 3.10+ 기준
- 타입 힌트 사용
- FastAPI + uvicorn
- 환경 변수로 설정 관리 (API 키 등)
- 무료 티어 제약을 항상 고려하여 리소스 효율적인 코드 작성

### 프론트엔드 (Next.js)
- Next.js 14+ (App Router)
- TypeScript 필수
- 정적 빌드 (output: 'export') → FastAPI에서 서빙
- Tailwind CSS 사용
- 채팅 UI는 스트리밍 응답 지원 (SSE)

### Docker (HF Spaces)
- 멀티스테이지 빌드: Node.js → Next.js 빌드 → Python 런타임
- 포트 7860 필수 (HF Spaces 요구사항)
- 모델은 빌드 시 또는 첫 실행 시 huggingface_hub로 다운로드

---

## 📊 현재 프로젝트 상태

### ✅ 완료된 구현
1. **백엔드 (backend/)**
   - FastAPI 서버 (main.py): RAG 파이프라인 + 정적 파일 서빙
   - API 모듈:
     - chat.py: 채팅 엔드포인트 (RAG + LLM 추론)
     - search.py: 하이브리드 검색 엔드포인트 (BM25 + 벡터)
   - 핵심 모듈 (core/):
     - embeddings.py: multilingual-e5-large 로더
     - llm.py: llama-cpp-python 기반 Qwen2.5-7B 추론
     - retriever.py: 하이브리드 검색 (BM25 + 벡터)
     - rag_service.py: 공통 RAG 파이프라인 서비스
     - prompts.py: 시스템 프롬프트 + RAG 템플릿 + 면책 고지
   - requirements.txt: 최적화된 의존성 (CPU-only torch)

2. **프론트엔드 (frontend/)**
   - Next.js 14 App Router: 정적 빌드 (output: 'export')
   - 채팅 UI: ChatWindow.tsx, MessageBubble.tsx
   - 면책 고지: Disclaimer.tsx
   - 스타일: TypeScript + Tailwind CSS

3. **데이터 (data/)**
   - 수집 클라이언트: law_go_kr.py (law.go.kr API 래퍼)
   - 수집 스크립트: collect_labor_laws.py (5개 노동법 수집)
   - 처리 파이프라인: index_labor_laws.py (청킹 + 임베딩 + 인덱싱)
   - 샘플 데이터: labor_laws.jsonl (5 documents)

4. **벡터DB (vectordb/)**
   - ChromaDB 저장소: 5개 문서 인덱싱 완료
   - 임베딩: 1024 dimensions (multilingual-e5-large)
   - 검색: 하이브리드 (BM25 + 벡터 검색)

5. **배포 (Dockerfile)**
   - 멀티스테이지 빌드: Node.js 20 → Python 3.11
   - git 설치 (모델 다운로드용)
   - 포트 7860 (HF Spaces 표준)
   - HEALTHCHECK: /api/health 엔드포인트

6. **버전 관리 (Git)**
   - GitHub 리포지토리: buelmanager/law
   - 커밋: 38 files, 2402 insertions
   - 마지막 커밋: "docs: Add detailed HF Spaces deployment guide"

### 🟡 다음 단계: HuggingFace Spaces 배포
- Space 생성: `korean-law-chatbot` (Docker, CPU 16GB)
- GitHub 리포지토리 연결 후 자동 빌드 예정

### 📈 배포 예상 타임라인
| 단계 | 시간 | 상태 |
|------|------|------|
| Docker 빌드 | 2-3분 | 대기 중 |
| 서버 시작 | 30초 | 대기 중 |
| 첫 모델 다운로드* | 2-3분 | 첫 채팅 시 발생 |
| 이후 응답 | 3-8초 | 정상 속도 |

*Qwen2.5-7B GGUF (~4GB) + multilingual-e5-large (~2GB)

### 🔗 배포 리소스
- **배포 가이드**: HF_SPACES_DEPLOYMENT.md
- **체크리스트**: DEPLOYMENT_CHECKLIST.md
- **상세 문서**: DEPLOYMENT.md
- **GitHub**: https://github.com/buelmanager/law (main branch)

### ⚡ 핵심 명세 (확정)
- **LLM**: Qwen2.5-7B-Instruct GGUF 4-bit (llama-cpp-python)
- **임베딩**: intfloat/multilingual-e5-large (1024 dims)
- **검색**: Hybrid (BM25 + 벡터 검색)
- **VectorDB**: ChromaDB (영구 저장, ./vectordb/)
- **백엔드**: FastAPI uvicorn (포트 7860)
- **프론트엔드**: Next.js 14 App Router (정적 빌드)
- **배포**: HF Spaces Docker (16GB RAM, 무료)
- **면책**: 모든 답변에 법률 정보 서비스 고지 포함
