from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run
from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.core.config import settings
from dotenv import load_dotenv

load_dotenv()

class AppCreator:
    
    @staticmethod
    def create_app() -> FastAPI:
        """
        Factory 模式创建 FastAPI 应用，便于测试 / 复用。
        """
        app = FastAPI(
            title="Travel Buddy AI", 
            version="0.1.0",
            description="AI-powered travel companion service"
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
            return {"status": "ok", "service": "Travel Buddy AI"}

        return app

if __name__ == "__main__":
    app = AppCreator.create_app()
    
    uvicorn_run(
        "travel_buddy_ai.main:AppCreator.create_app",  # 修正工厂函数路径
        host=settings.host,
        port=settings.port,
        factory=True,      # 让 uvicorn 调用 create_app()
        reload=True,       # 开发自动热重载
        log_level="info",  # 设置日志级别
    )
