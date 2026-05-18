"""App FastAPI principal."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from slowapi.util import get_remote_address

# Prometheus metrics (T128-T129)
COLLECTOR_DURATION = Histogram("lottery_download_duration_seconds", "Download duration per game", ["game"])
COLLECTOR_NEW = Counter("lottery_new_contests_total", "New contests found", ["game"])
COLLECTOR_ERRORS = Counter("lottery_errors_total", "Collector errors", ["game", "type"])

from lucky_number.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Lucky Number",
    description="Gera combinações de números aleatórios para loterias da Caixa que nunca foram sorteadas",
    version="0.1.0", docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)

# Rate limiting (T042) — Prevents CWE-400 (disabled in test env)
if os.getenv("ENVIRONMENT") != "test":
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# CORS (T043) — disabled in test env
if os.getenv("ENVIRONMENT") != "test":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# TrustedHost (T044) — disabled in test env
if os.getenv("ENVIRONMENT") != "test":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", ".luckynumber.app"])

app.include_router(router, prefix="/api/v1")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type="text/plain")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(str(index_path))
    return {"message": "Lucky Number API", "docs": "/docs", "jogos": "/api/v1/jogos-disponiveis"}


def main():
    import uvicorn
    uvicorn.run("lucky_number.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
