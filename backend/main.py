import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# API 라우터
from api.chat import router as chat_router
from api.search import router as search_router

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
        from core.embeddings import EmbeddingsManager
        from core.retriever import Retriever
        from core.llm import LLMManager

        embeddings_model = os.getenv("EMBEDDINGS_MODEL_NAME", "intfloat/multilingual-e5-large")
        chroma_path = os.getenv("CHROMADB_PATH", "./vectordb")
        llm_model_path = os.getenv("LLM_MODEL_PATH", "./models/qwen2.5-7b-instruct-q4_k_m.gguf")

        # Embeddings
        try:
            app_state.embeddings = EmbeddingsManager(model_name=embeddings_model)
        except Exception as e:
            logger.warning(f"Failed to init EmbeddingsManager: {e}")
            app_state.embeddings = None

        # Retriever
        try:
            app_state.retriever = Retriever(chroma_db_path=chroma_path)
        except Exception as e:
            logger.warning(f"Failed to init Retriever: {e}")
            app_state.retriever = None

        # LLM (only if model file exists)
        try:
            if os.path.exists(llm_model_path):
                app_state.llm = LLMManager(model_path=llm_model_path)
            else:
                logger.warning(f"LLM model not found at {llm_model_path}, skipping LLM init")
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

    logger.info("✅ 모든 모듈 초기화 완료 (가능한 항목)")
    yield
    logger.info("🛑 서버 종료")

app = FastAPI(
    title="AI 법률 상담 챗봇",
    description="RAG 기반 노동법 전문 상담",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(search_router, prefix="/api", tags=["search"])

# 헬스체크
@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "law-chatbot-api",
        "version": "0.1.0",
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
        port=7860,
        reload=True
    )
