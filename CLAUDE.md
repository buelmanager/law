# 프로젝트: 무료 클라우드 기반 오픈소스 AI 법률 상담 챗봇

## 프로젝트 개요

무료 클라우드 서버 환경에서 특정 법률 분야에 특화된 오픈소스 AI 법률 상담 챗봇을 구축하는 프로젝트.
사용자가 법률 질문을 입력하면, 관련 법령과 판례를 검색(RAG)하여 근거 기반 답변을 생성한다.

> **핵심 원칙**: 이 서비스는 "법률 정보 제공"이지 "법률 자문"이 아니다. 변호사법 위반 리스크를 피하기 위해 모든 답변에 면책 고지를 포함하고, 개별 사안에 대한 단정적 결론을 제시하지 않는다.

---

## 아키텍처

```
사용자 질문
    → 임베딩 (multilingual-e5-base, 768 dims)
    → 벡터DB 검색 (ChromaDB)
    → 관련 법령/판례 청크 추출
    → LLM 컨텍스트로 전달 (Groq API - open-mixtral-8x7b)
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
- **LLM**: Groq API (open-mixtral-8x7b) 또는 Mistral AI 폴백
  - 무료 API, 빠른 응답 속도
- **임베딩**: intfloat/multilingual-e5-base (768 dims, ~560MB)
  - 로컬 sentence-transformers 사용 (HF Inference API 지원 중단으로 변경)
  - e5-large (1024 dims) → e5-base (768 dims)로 다운그레이드 (메모리 최적화)
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

### 법제처 국가법령정보 공동활용 (Open API)
- **신청 페이지**: https://open.law.go.kr/LSO/openApi/cuAskList.do#
- **End Point**: `https://apis.data.go.kr/1170000/law`
- **데이터 포맷**: XML
- **인증키**: `b7edf147d2fa53dbafbd3417ea617dde15ddc9cbbe54d6c9a078b64012f801ae`
- **활용기간**: 2026-01-29 ~ 2028-01-29
- **일일 트래픽**: 10,000건/API
- **라이선스**: 저작자표시 (공공데이터)

#### 제공 API 목록
| API | 엔드포인트 | 설명 |
|-----|-----------|------|
| 법령정보 목록 조회 | `/lawSearchList.do` | 현행법령 목록 |
| 행정규칙정보 목록 조회 | `/admrulSearchList.do` | 현행행정규칙 목록 |
| 자치법규정보 목록 조회 | `/ordinSearchList.do` | 현행자치법규 목록 |
| 법령해석례정보 목록 조회 | `/expcSearchList.do` | 법령해석례 목록 |
| 헌재결정례정보 목록 조회 | `/detcSearchList.do` | 헌재결정례 목록 |
| 별표서식정보 목록 조회 | `/licbylSearchList.do` | 별표서식 목록 |
| 법령용어정보 목록 조회 | `/lstrmSearchList.do` | 법령용어 목록 |
| 조약정보 목록 조회 | `/trtySearchList.do` | 조약 목록 |

### 판례 데이터 (2026-01-29 기준)

#### 📊 수집 현황 요약

| 데이터 유형 | 수집 건수 | 청크 수 | 품질 |
|------------|----------|---------|------|
| 판례 | 1,438건 | ~3,500개 | ✅ 전문 100% |
| 법령해석례 | 492건 | ~1,500개 | ✅ 완전 |
| 노동법 법령 | 5건 | ~80개 | ✅ 완료 |
| **합계** | **1,935건** | **5,083개** | - |

#### 📜 판례 상세 (530건 상세 수집)

| 항목 | 건수 | 비율 | 설명 |
|------|------|------|------|
| 대법원 | 321건 | 60.6% | 최고법원 판결 |
| 고등법원 | 68건 | 12.8% | 항소심 판결 |
| 지방법원 | 141건 | 26.6% | 1심 판결 |
| 판시사항 있음 | 353건 | 66.6% | 핵심 법리 |
| 판결요지 있음 | 233건 | 44.0% | 결론 요약 |
| 전문 있음 | 530건 | 100% | 판결문 전체 |

#### 📋 법령해석례 상세 (164건)

| 항목 | 건수 | 비율 |
|------|------|------|
| 질의요지 | 164건 | 100% |
| 회답 | 164건 | 100% |
| 이유 | 164건 | 100% |

#### 🔍 데이터 출처 및 신뢰성

| 출처 | URL | 라이선스 | 신뢰도 |
|------|-----|----------|--------|
| 법제처 국가법령정보 | law.go.kr/DRF | 공공저작물 (CC BY) | ⭐⭐⭐⭐⭐ |
| 대법원 공개 판례 | (API 경유) | 공공저작물 | ⭐⭐⭐⭐⭐ |

**데이터 정확도**:
- 모든 판례는 **법제처 공식 API**에서 수집
- 판례번호, 선고일자, 법원명 등 메타데이터 **100% 정확**
- 판시사항/판결요지는 법원 제공 원본 그대로 사용

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

## 4대 특화 분야

생활 밀착형 4대 법률 분야에 특화된 전문 상담 서비스를 제공합니다.

### 1. 노동법
- **상담 주제**: 부당해고, 임금체불, 퇴직금, 연차휴가, 직장 내 괴롭힘
- **주요 법령**: 근로기준법, 근로자퇴직급여보장법, 남녀고용평등법, 최저임금법, 산업재해보상보험법

### 2. 임대차법
- **상담 주제**: 보증금 반환, 계약갱신, 차임인상, 대항력/우선변제권, 상가임대차
- **주요 법령**: 주택임대차보호법, 상가건물임대차보호법, 민법 임대차

### 3. 소비자보호법
- **상담 주제**: 환불/청약철회, 제품 하자, 불공정 약관, 온라인 거래, 소비자 분쟁조정
- **주요 법령**: 소비자기본법, 전자상거래법, 약관규제법, 할부거래법

### 4. 교통사고·손해배상
- **상담 주제**: 과실비율, 손해배상 산정, 보험금 청구, 후유장해, 형사/민사 절차
- **주요 법령**: 자동차손해배상보장법, 도로교통법, 교통사고처리특례법

> 4개 분야에 관련된 20개 이상의 핵심 법령과 대법원 판례가 인덱싱되어 있습니다.

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
     - embeddings.py: multilingual-e5-base 로컬 로더 (sentence-transformers)
     - llm.py: Groq API 기반 LLM 추론
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
   - ChromaDB 저장소: **~3,000개 청크** 목표 (빌드 시 생성)
   - 4개 분야: 노동법, 임대차법, 소비자보호법, 교통사고
   - 임베딩: 768 dimensions (multilingual-e5-base, 로컬)
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

### ✅ HuggingFace Spaces 배포 완료
- **Space URL**: https://wonchulhee-korean-law-chatbot.hf.space
- **상태**: 운영 중 (degraded - 모델 로딩 시 정상화)
- **Health Check**: https://wonchulhee-korean-law-chatbot.hf.space/api/health

### 📈 배포 타임라인
| 단계 | 시간 | 상태 |
|------|------|------|
| Docker 빌드 | 2-3분 | ✅ 완료 |
| 서버 시작 | 30초 | ✅ 완료 |
| 모델 로딩 | 2-3분 | ⏳ 첫 채팅 시 |
| 이후 응답 | 3-8초 | 정상 속도 |

### 🔗 배포 리소스
- **배포 가이드**: HF_SPACES_DEPLOYMENT.md
- **체크리스트**: DEPLOYMENT_CHECKLIST.md
- **상세 문서**: DEPLOYMENT.md
- **GitHub**: https://github.com/buelmanager/law (main branch)

---

## 🌐 웹 랜딩 페이지 (web/)

### 배포 정보
- **랜딩 페이지 URL**: https://law-ai-chat.vercel.app
- **챗봇 URL**: https://wonchulhee-korean-law-chatbot.hf.space
- **플랫폼**: Vercel (랜딩) + HuggingFace Spaces (챗봇)
- **GitHub**: buelmanager/law (main branch)

### 기술 스택
- **HTML/CSS/JS**: 정적 사이트 (프레임워크 없음)
- **애니메이션**: GSAP 3.12 + ScrollTrigger
- **스크롤**: Lenis Smooth Scroll
- **아이콘**: Lucide Icons (SVG)
- **파티클**: Canvas API (블루 테마)
- **폰트**: Pretendard

### 디자인 시스템
```css
/* 컬러 팔레트 */
--color-bg-primary: #0a0f1a;      /* Deep Navy */
--color-bg-secondary: #0f172a;
--color-primary: #3b82f6;          /* Blue */
--color-primary-light: #60a5fa;
--color-gold: #f59e0b;             /* 강조/경고 */
--color-emerald: #10b981;          /* 상태 표시 */
```

### 페이지 구조
1. **Hero**: 4대 특화 분야 배지 + 챗봇 UI (첫 메시지 시 전체폭 확장)
2. **Trust Indicators**: 신뢰 지표 (4개 카드 - 특화분야, 법령수, 판례, 프라이버시)
3. **How It Works**: RAG 프로세스 시각화 (4단계)
4. **Categories**: 4대 특화 분야 카드 (노동법, 임대차법, 소비자보호법, 교통사고)
5. **Disclaimer**: 법률 정보 서비스 면책 고지
6. **FAQ**: 자주 묻는 질문 (5개)
7. **Footer**: 브랜딩 + 링크

### 파일 구조
```
web/
├── index.html      # 메인 HTML (LawBot 브랜딩, 4대 분야)
├── contact.html    # 무료 상담 신청 페이지 (Webform 연동 준비)
├── styles.css      # 전체 스타일 (CSS 변수, 반응형, 블루 테마)
└── script.js       # GSAP 애니메이션, Lucide 초기화, 채팅 로직
```

### 아이콘 시스템
```html
<!-- Lucide Icons 사용법 -->
<i data-lucide="scale" class="icon-lg"></i>

<!-- 사이즈 클래스 -->
.icon-xs: 14px
.icon-sm: 18px
.icon: 22px
.icon-md: 28px
.icon-lg: 36px
.icon-xl: 48px
```

### 4대 분야 컬러 코드
```css
/* 분야별 색상 */
.labor    { color: #3b82f6; }  /* 노동법 - 블루 */
.housing  { color: #10b981; }  /* 임대차법 - 그린 */
.consumer { color: #f59e0b; }  /* 소비자보호법 - 골드 */
.traffic  { color: #ef4444; }  /* 교통사고 - 레드 */
```

### 주요 컴포넌트
- **Glass Card**: `backdrop-filter: blur(16px)` + 반투명 배경
- **Area Badge**: 분야별 컬러 배지 (hero-areas)
- **Trust Card**: 신뢰 지표 표시 카드
- **RAG Step**: 프로세스 단계 표시
- **Category Area Card**: 4대 분야 상세 카드 (분야별 아이콘/컬러)
- **Contact Form**: 상담 신청 폼 (Webform 연동 준비)

### 채팅창 확장 기능
```javascript
// 첫 메시지 전송 시 채팅창 전체폭 확장
const heroSection = document.querySelector('.hero.hero-with-chat');
if (heroSection && !heroSection.classList.contains('chat-fullwidth')) {
    heroSection.classList.add('chat-fullwidth');
}
```

### 배포 명령어
```bash
cd web
npx vercel --prod
```

### ⚡ 핵심 명세 (확정)
- **LLM**: Groq API (open-mixtral-8x7b) 또는 Mistral AI 폴백
- **임베딩**: intfloat/multilingual-e5-base (768 dims, 로컬 sentence-transformers)
- **검색**: Hybrid (BM25 + 벡터 검색)
- **VectorDB**: ChromaDB (영구 저장, ./vectordb/)
- **백엔드**: FastAPI uvicorn (포트 7860)
- **프론트엔드**: Next.js 14 App Router (정적 빌드)
- **배포**: HF Spaces Docker (16GB RAM, 무료)
- **면책**: 모든 답변에 법률 정보 서비스 고지 포함

---

## 🔖 버전 관리

### 현재 버전
- **APP_VERSION**: `0.5.0`
- **BUILD_ID**: `e5-base-4cat`
- **BUILD_DATE**: `2026-01-29`

### 버전 확인 방법
1. **로그 확인** - HF Spaces 로그에서 서버 시작 시 버전 출력
   ```
   ============================================================
   🚀 서버 시작
   📦 버전: 0.5.0 | 빌드: e5-base-4cat | 날짜: 2026-01-29
   ============================================================
   ```

2. **API 엔드포인트** - `/api/health` 호출
   ```bash
   curl https://wonchulhee-korean-law-chatbot.hf.space/api/health
   ```
   응답:
   ```json
   {
     "version": "0.5.0",
     "build_id": "e5-base-4cat",
     "build_date": "2026-01-29"
   }
   ```

### 버전 업데이트 시
`backend/main.py` 상단의 다음 변수를 수정:
```python
APP_VERSION = "0.5.0"
BUILD_DATE = "2026-01-29"
BUILD_ID = "e5-base-4cat"
```

---

## 🔧 기술 변경 이력

### 2026-01-29: 임베딩 모델 변경 (v0.5.0)

#### 문제 상황
- HuggingFace Inference API (`api-inference.huggingface.co`) 완전 지원 중단
- `410 Client Error: Gone` 오류 발생
- 새 API (`router.huggingface.co/hf-inference`)도 직접 REST 호출 미지원

#### 해결책
- **외부 API → 로컬 모델**로 전환
- `sentence-transformers` 라이브러리 사용
- 모델: `intfloat/multilingual-e5-base` (768 dims, ~560MB)

#### 임베딩 모델 비교
| 모델 | 차원 | 크기 | 메모리 | 선택 |
|------|------|------|--------|------|
| e5-small | 384 | ~120MB | 낮음 | ❌ 품질 부족 |
| **e5-base** | **768** | **~560MB** | **중간** | ✅ **채택** |
| e5-large | 1024 | ~2.2GB | 높음 | ❌ OOM 위험 |

#### 현재 빌드 설정 (Dockerfile)
```dockerfile
# 4개 분야, ~3000 청크 목표
RUN python data/collect/collect_all_categories.py \
    --enable-category labor,lease,consumer,traffic \
    --all-enabled \
    --max-items 30 \
    --detail-limit 60 \
    && python data/process/index_cases.py --collection law_cases
```

#### 관련 파일
- `backend/core/embeddings.py`: 로컬 sentence-transformers 사용
- `data/process/index_cases.py`: 인덱싱 시 로컬 모델 사용
- `Dockerfile`: 빌드 시 데이터 수집 + 인덱싱

### Git 리모트 설정
```bash
# GitHub (origin)
git remote add origin https://github.com/buelmanager/law.git

# HuggingFace Spaces (hf)
git remote add hf https://huggingface.co/spaces/wonchulhee/korean-law-chatbot

# 양쪽에 푸시
git push origin main && git push hf main
```
