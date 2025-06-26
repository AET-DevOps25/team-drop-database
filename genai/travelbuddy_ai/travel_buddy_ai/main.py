from fastapi import FastAPI
from uvicorn import run as uvicorn_run
from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.config import settings
from dotenv import load_dotenv

load_dotenv()

def create_app() -> FastAPI:
    """
    Factory 模式创建 FastAPI 应用，便于测试 / 复用。
    """
    app = FastAPI(title="Travel Buddy AI", version="0.1.0")
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health", tags=["_infra"])
    async def health():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    uvicorn_run(
        "travel_buddy_ai.main:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,      # 让 uvicorn 调用 create_app()
        reload=True,       # 开发自动热重载
    )
