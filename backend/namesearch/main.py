"""Main FastAPI application module."""
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from . import models
from .api.v1.api import api_router
from .core.config import settings
from .db.session import engine, SessionLocal
from .services.domain_monitor import get_domain_monitor
from .db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize domain monitor
    monitor = get_domain_monitor()
    asyncio.create_task(monitor.start())
    yield
    # Shutdown: Clean up
    await monitor.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Namesearch.io - AI-powered brand and domain name intelligence",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add middleware to log and handle CORS requests
@app.middleware("http")
async def log_cors_requests(request: Request, call_next):
    # Log incoming requests for debugging
    print(f"Incoming request - Method: {request.method}, Path: {request.url.path}, Origin: {request.headers.get('origin')}")
    
    # Handle preflight requests
    if request.method == "OPTIONS":
        print(f"CORS Preflight Request - Origin: {request.headers.get('origin')}")
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            status_code=200,
            content={"message": "CORS preflight successful"},
        )
    else:
        response = await call_next(request)
    
    # Add CORS headers to all responses
    origin = request.headers.get('origin')
    if origin and origin in [str(o) for o in settings.CORS_ORIGINS]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    print(f"Allowed Origins: {settings.CORS_ORIGINS}")
    return response

# Include API routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "namesearch.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else None,
    )
