"""Application factory — wires middleware, routers, lifecycle."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import auth, evaluation, evaluation_cases, health, n8n, state


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
    app.include_router(n8n.router)
    app.include_router(auth.router)
    app.include_router(state.router)

    return app
