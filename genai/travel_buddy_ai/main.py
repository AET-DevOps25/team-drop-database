from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run
from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger
from dotenv import load_dotenv


logger = get_logger(__name__)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Application starting up...")
    yield  # During application runtime
    logger.info("🔄 Application shutting down...")


class AppCreator:
    
    @staticmethod
    def create_app() -> FastAPI:
        """
        Factory pattern to create FastAPI app, convenient for testing / reuse.
        """
        app = FastAPI(
            title="Travel Buddy AI", 
            version="0.1.0",
            description="AI-powered travel companion service",
            lifespan=lifespan  # 使用新的 lifespan 事件处理器
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Should set specific domains in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        app.include_router(v1_router, prefix="/api/v1")

        @app.get("/health", tags=["_infra"])
        async def health():
            qa_ready = hasattr(app.state, 'qa_system') and app.state.qa_system is not None
            vector_ready = hasattr(app.state, 'vector_service') and app.state.vector_service is not None
            return {
                "status": "ok", 
                "service": "Travel Buddy AI",
                "qa_system": "ready" if qa_ready else "not_initialized",
                "vector_service": "ready" if vector_ready else "not_initialized"
            }

        return app

if __name__ == "__main__":
    app = AppCreator.create_app()
    
    uvicorn_run(
        "travel_buddy_ai.main:AppCreator.create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=True,
        log_level="info",
    )
