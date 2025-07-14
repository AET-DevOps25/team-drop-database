from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run
from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger
from travel_buddy_ai.core.state import app_state  # Import state management
from dotenv import load_dotenv

from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

logger = get_logger(__name__)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    
    # Initialize on startup
    try:
        logger.info("🧪 Starting Q&A system initialization...")
        qa_system = AttractionQASystem()
        app_state.set_qa_system(qa_system)  # Set to global state
        logger.info("✅ Q&A system initialized successfully")
    except Exception as e:
        logger.error(f"❌ QA system initialization failed: {e}")
        app_state.set_qa_system(None)
    
    yield  # During application runtime
    
    # Cleanup resources on shutdown (if needed)
    logger.info("🔄 Application shutting down, cleaning up resources...")

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
            qa_system = app_state.get_qa_system()
            return {
                "status": "ok", 
                "service": "Travel Buddy AI",
                "qa_system": "ready" if qa_system else "not_initialized"
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
