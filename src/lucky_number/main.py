"""App FastAPI principal."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from lucky_number.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Lucky Number",
    description="Gera combinações de números aleatórios para loterias da Caixa que nunca foram sorteadas",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router, prefix="/api/v1")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    """Serve a interface web."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(str(index_path))
    return {
        "message": "Lucky Number API",
        "docs": "/docs",
        "jogos": "/api/v1/jogos-disponiveis",
    }


def main():
    """Executa o servidor de desenvolvimento."""
    import uvicorn
    uvicorn.run(
        "lucky_number.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
