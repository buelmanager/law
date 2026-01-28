import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# API 라우터
from backend.api.chat import router as chat_router
from backend.api.search import router as search_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 앱 상태 관리
class AppState:
    def __init__(self):
        self.llm = None
        self.retriever = None
        self.embeddings = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션 라이프사이클 관리"""
    logger.info("🚀 서버 시작")
    
    # 모델 초기화 시도 (환경변수 또는 기본값 사용)
    try:
        from backend.core.embeddings import EmbeddingsManager
        from backend.core.retriever import Retriever
        from backend.core.llm import LLMManager

        embeddings_model = os.getenv("EMBEDDINGS_MODEL_NAME", "intfloat/multilingual-e5-large")
        chroma_path = os.getenv("CHROMADB_PATH", "./vectordb")

        # Embeddings
        try:
            app_state.embeddings = EmbeddingsManager(model_name=embeddings_model)
        except Exception as e:
            logger.warning(f"Failed to init EmbeddingsManager: {e}")
            app_state.embeddings = None

        # Retriever
        try:
            app_state.retriever = Retriever(chroma_db_path=chroma_path)

            # Check if collection is empty and auto-index if needed
            if app_state.retriever.collection is None or (
                app_state.retriever.collection and app_state.retriever.collection.count() == 0
            ):
                logger.info("Collection empty or not found, attempting auto-indexing...")
                try:
                    from backend.core.auto_indexer import auto_index_labor_laws
                    auto_index_labor_laws(app_state.retriever, app_state.embeddings)
                    logger.info("Auto-indexing complete!")
                except Exception as idx_err:
                    logger.warning(f"Auto-indexing failed: {idx_err}")
        except Exception as e:
            logger.warning(f"Failed to init Retriever: {e}")
            app_state.retriever = None

        # LLM (Groq API)
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                app_state.llm = LLMManager(api_key=groq_api_key)
            else:
                logger.warning("GROQ_API_KEY not set, LLM will not be available")
                app_state.llm = None
        except Exception as e:
            logger.warning(f"Failed to init LLMManager: {e}")
            app_state.llm = None

        # Attach to app.state for request-time access
        app.state.embeddings = app_state.embeddings
        app.state.retriever = app_state.retriever
        app.state.llm = app_state.llm

    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")

    # 초기화 상태 요약
    init_status = {
        "embeddings": app_state.embeddings is not None,
        "retriever": app_state.retriever is not None,
        "llm": app_state.llm is not None,
    }
    logger.info(f"✅ 모듈 초기화 상태: {init_status}")

    if not init_status["embeddings"] or not init_status["retriever"]:
        logger.warning("⚠️ 필수 모듈(embeddings, retriever) 미초기화 - RAG 기능 제한됨")

    yield
    logger.info("🛑 서버 종료")

app = FastAPI(
    title="AI 법률 상담 챗봇",
    description="RAG 기반 노동법 전문 상담",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 (보안 강화)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "https://wonchulhee-korean-law-chatbot.hf.space",
    "https://huggingface.co",
    "http://localhost:3000",  # 개발용
    "http://localhost:7860",  # 개발용
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# API 라우터 등록
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(search_router, prefix="/api", tags=["search"])

# 헬스체크
@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트 - 모듈 상태 포함"""
    modules_ready = {
        "embeddings": app_state.embeddings is not None,
        "retriever": app_state.retriever is not None,
        "llm": app_state.llm is not None,
    }

    # 필수 모듈(embeddings, retriever) 중 하나라도 없으면 degraded 상태
    is_fully_ready = modules_ready["embeddings"] and modules_ready["retriever"]

    return {
        "status": "healthy" if is_fully_ready else "degraded",
        "service": "law-chatbot-api",
        "version": "0.1.0",
        "modules": modules_ready,
    }

# Next.js 정적 파일 서빙 (빌드 결과물)
frontend_build_dir = Path(__file__).parent.parent / "frontend" / "out"
if frontend_build_dir.exists():
    logger.info(f"Mounting static files from: {frontend_build_dir}")
    app.mount("/", StaticFiles(directory=str(frontend_build_dir), html=True), name="static")
else:
    logger.warning(f"Frontend build directory not found: {frontend_build_dir}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port} (debug={debug})")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
    )
