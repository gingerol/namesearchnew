"""API router configuration."""
from fastapi import APIRouter

from .endpoints import (
    auth, users, domains, searches, watches, notifications
)

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(domains.router, prefix="/domains", tags=["Domains"])
api_router.include_router(searches.router, prefix="/searches", tags=["Searches"])
api_router.include_router(watches.router, prefix="/watches", tags=["Domain Watches"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
