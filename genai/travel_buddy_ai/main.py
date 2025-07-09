from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run
from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger
from travel_buddy_ai.core.state import app_state  # 导入状态管理
from dotenv import load_dotenv

from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem

logger = get_logger(__name__)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    
    # 启动时初始化
    try:
        logger.info("🧪 开始初始化问答系统...")
        qa_system = AttractionQASystem()
        app_state.set_qa_system(qa_system)  # 设置到全局状态
        logger.info("✅ 问答系统初始化成功")
    except Exception as e:
        logger.error(f"❌ QA系统初始化失败: {e}")
        app_state.set_qa_system(None)
    
    yield  # 应用运行期间
    
    # 关闭时清理资源（如果需要的话）
    logger.info("🔄 应用关闭，清理资源...")

class AppCreator:
    
    @staticmethod
    def create_app() -> FastAPI:
        """
        Factory 模式创建 FastAPI 应用，便于测试 / 复用。
        """
        app = FastAPI(
            title="Travel Buddy AI", 
            version="0.1.0",
            description="AI-powered travel companion service",
            lifespan=lifespan  # 使用新的 lifespan 事件处理器
        )
        
        # 添加 CORS 中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境中应该设置具体的域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
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
