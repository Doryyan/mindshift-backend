from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.config import settings
from app.database import init_db
from app.routers import (
    auth, courses, cases, roleplay, community, training,
    membership, progress, growth, referral as referral_router,
)
from app.routers.recommendations import router as recommendations_router
from app.routers.dashboard import router as dashboard_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="念转 MindShift — NLP语言教练后端API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Simple rate limiting — production should use Redis
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION, "timestamp": time.time()}

@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION}

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(cases.router)
app.include_router(roleplay.router)
app.include_router(community.router)
app.include_router(training.router)
app.include_router(membership.router)
app.include_router(progress.router)
app.include_router(growth.router)
app.include_router(recommendations_router)
app.include_router(referral_router.router)
app.include_router(dashboard_router)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "error": str(exc) if settings.DEBUG else ""},
    )

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")

@app.on_event("shutdown")
async def shutdown():
    logger.info(f"{settings.APP_NAME} shutting down")
# Serve admin dashboard with HTTP Basic Auth
import base64
from fastapi.responses import HTMLResponse
from fastapi import Request
import os

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return HTMLResponse("Unauthorized", status_code=401,
            headers={"WWW-Authenticate": "Basic realm=\"MindShift Admin\""})
    try:
        decoded = base64.b64decode(auth.split(" ")[1]).decode()
        u, p = decoded.split(":", 1)
    except:
        return HTMLResponse("Invalid auth", status_code=401)
    if u != "admin" or p != "MindShift2026":
        return HTMLResponse("Wrong credentials", status_code=401)
    fp = os.path.join(os.path.dirname(__file__), "static", "admin_dashboard.html")
    if os.path.exists(fp):
        with open(fp) as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Dashboard not found</h1>")
    return "<h1>Dashboard file not found</h1>"
