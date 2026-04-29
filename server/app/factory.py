"""Application factory — wires middleware, routers, lifecycle."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.config import CORS_ORIGINS
from app.routers import auth, evaluation, evaluation_cases, evaluation_results, health, n8n, state

# Repo root: server/app/factory.py → parent.parent.parent
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    app = FastAPI(title="BVAB Eval API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(evaluation.router)
    app.include_router(evaluation_cases.router)
    app.include_router(evaluation_results.router)
    app.include_router(n8n.router)
    app.include_router(auth.router)
    app.include_router(state.router)

    @app.get("/")
    def serve_index():
        index = _PROJECT_ROOT / "index.html"
        if index.is_file():
            return FileResponse(index, media_type="text/html; charset=utf-8")
        return JSONResponse(
            {"detail": "index.html not found at project root"},
            status_code=404,
        )

    return app
