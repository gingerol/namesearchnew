"""CRUD operations package."""
from .base import CRUDBase
from .crud_user import user
from .crud_domain import domain
from .crud_project import project

__all__ = ["CRUDBase", "user", "domain", "project"]
