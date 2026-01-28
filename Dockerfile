# 멀티스테이지 빌드: Node.js → Next.js 빌드
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build

# 메인 이미지: Python 런타임
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY backend/ ./backend/

# 데이터 복사
COPY data/ ./data/

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# vectordb 디렉토리 생성 및 초기화
RUN mkdir -p ./vectordb && \
    echo "VectorDB will be initialized on first run or can be pre-populated" > ./vectordb/README.txt

# 빌드 시 vectordb 생성 (선택적 - 주석 처리됨)
# 주석 해제하면 빌드 시 자동으로 인덱싱 (빌드 시간 +2-3분)
# RUN python data/process/index_labor_laws.py

# 포트 설정 (HuggingFace Spaces 필수)
EXPOSE 7860

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# 백엔드 실행
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
