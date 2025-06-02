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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
