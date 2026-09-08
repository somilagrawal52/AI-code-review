from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.api.routes import analytics, auth, repositories, reviews, webhooks
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.demo_mode and settings.database_url.startswith("sqlite"):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="CodeSage AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Hub-Signature-256",
        "X-GitHub-Delivery",
        "X-GitHub-Event",
    ],
)
app.include_router(auth.router)
app.include_router(repositories.router)
app.include_router(reviews.router)
app.include_router(analytics.router)
app.include_router(webhooks.router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok", "demo_mode": settings.demo_mode}
