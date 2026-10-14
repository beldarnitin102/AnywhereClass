
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import (
    APP_NAME,
    APP_VERSION,
    FRONTEND_ORIGIN,
)
from app.db.base import Base
from app.db.session import engine
from app import models  # Registers SQLAlchemy models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Temporary for local development only.
    # Alembic migrations will replace this schema creation.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": f"{APP_NAME} API is running"}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }
