# ===========================================
# Stage 1: Node.js - Next.js 프론트엔드 빌드
# ===========================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ===========================================
# Stage 2: Python 빌드 환경 (컴파일 도구 포함)
# ===========================================
FROM python:3.11-slim AS python-builder

WORKDIR /app

# 빌드 도구 설치 (llama-cpp-python 컴파일용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY backend/requirements.txt .

# CPU 전용 PyTorch + 의존성 설치
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt

# ===========================================
# Stage 3: 최종 런타임 이미지 (경량)
# ===========================================
FROM python:3.11-slim

WORKDIR /app

# 런타임 필수 패키지만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 패키지 복사
COPY --from=python-builder /app/packages /usr/local/lib/python3.11/site-packages/

# 백엔드 코드 복사
COPY backend/ ./backend/

# 데이터 복사
COPY data/ ./data/

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# 사전 빌드된 벡터DB 복사 (인덱싱된 법령 데이터)
COPY vectordb/ ./vectordb/

# models 디렉토리 생성 (LLM 모델은 첫 실행 시 자동 다운로드)
RUN mkdir -p ./models

# 포트 설정 (HuggingFace Spaces 필수)
EXPOSE 7860

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV PYTHONPATH=/app

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# 백엔드 실행
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
