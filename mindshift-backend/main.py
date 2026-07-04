from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MindShift API...")
    await init_db()
    logger.info("Database tables created.")
    yield
    logger.info("Shutting down MindShift API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# GZip compression middleware - compress responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response timing middleware - log requests taking > 3 seconds
@app.middleware("http")
async def response_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    if process_time > 3.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"completed in {process_time:.2f}s (status={response.status_code})"
        )

    response.headers["X-Process-Time"] = f"{process_time:.2f}s"
    return response


app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}
