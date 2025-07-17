# main.py
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvicorn_run
from dotenv import load_dotenv

# Prometheus client
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, collect_default_metrics

from travel_buddy_ai.api.v1 import router as v1_router
from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

# --- Prometheus metrics definitions ---

# HTTP request metrics
REQUEST_COUNT = Counter(
    'llm_api_requests_total',
    'Total HTTP requests received',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'llm_api_request_latency_seconds',
    'Latency of HTTP requests',
    ['method', 'endpoint']
)
REQUEST_ERRORS = Counter(
    'llm_api_request_errors_total',
    'Total HTTP request errors',
    ['method', 'endpoint']
)

# LLM inference metrics (to be used inside your LLM handlers)
LLM_INFERENCE_LATENCY = Histogram(
    'llm_inference_duration_seconds',
    'Time spent in LLM model inference',
    ['model_name']
)
LLM_INFERENCE_ERRORS = Counter(
    'llm_inference_errors_total',
    'Errors during LLM model inference',
    ['model_name']
)

# Collect default process metrics (CPU, GC, etc.)
collect_default_metrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

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
            lifespan=lifespan
        )

        # 1) CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 2) Prometheus HTTP middleware
        @app.middleware("http")
        async def prometheus_middleware(request: Request, call_next):
            method = request.method
            endpoint = request.url.path
            start = time.time()
            try:
                response: Response = await call_next(request)
                status_code = response.status_code
            except Exception as e:
                # Count as error
                REQUEST_ERRORS.labels(method=method, endpoint=endpoint).inc()
                status_code = 500
                raise
            finally:
                # Observe latency
                latency = time.time() - start
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
                # Count request
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    http_status=str(status_code)
                ).inc()
            return response

        # 3) Register API routes
        app.include_router(v1_router, prefix="/api/v1")

        # 4) Health check
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

        # 5) Prometheus scrape endpoint
        @app.get("/metrics", tags=["_infra"])
        async def metrics():
            data = generate_latest()
            return Response(content=data, media_type=CONTENT_TYPE_LATEST)

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
