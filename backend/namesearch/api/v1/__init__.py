"""API v1 package."""
from fastapi import APIRouter

from .endpoints import auth, users, domains, projects, searches, admin
from .deps import get_db, get_current_user, get_current_active_user, get_current_active_superuser

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(searches.router, prefix="/searches", tags=["searches"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Export dependencies
__all__ = [
    'get_db',
    'get_current_user',
    'get_current_active_user',
    'get_current_active_superuser',
]
