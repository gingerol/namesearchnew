"""API v1 endpoints package."""
from .auth import router as auth_router
from .users import router as users_router
from .domains import router as domains_router
from .projects import router as projects_router
from .searches import router as searches_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "domains_router",
    "projects_router",
    "searches_router",
    "admin_router",
]
