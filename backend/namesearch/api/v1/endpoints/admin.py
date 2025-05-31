"""Admin dashboard endpoints for analytics, logs, and API key management."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .... import crud, models
from ....core.security import get_current_active_superuser
from ....db.session import get_db

router = APIRouter()

@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get high-level stats for admin dashboard (user count, project count, etc).
    """
    user_count = crud.user.count(db)
    project_count = crud.project.count(db)
    # TODO: Add more stats (active users, searches, etc)
    return {
        "user_count": user_count,
        "project_count": project_count,
    }

@router.get("/users", response_model=List[models.User])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    List all users (admin only).
    """
    return crud.user.get_multi(db)

@router.get("/projects", response_model=List[models.Project])
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    List all projects (admin only).
    """
    return crud.project.get_multi(db)

@router.get("/logs", response_model=List[dict])
def get_system_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get recent system logs (stub).
    """
    # TODO: Integrate with real logging system (ELK/Loki)
    return [{"timestamp": "2025-05-30T23:59:00Z", "message": "System started"}]

@router.get("/api-keys", response_model=List[dict])
def get_api_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    List all API keys (stub).
    """
    # TODO: Integrate with API key management
    return [{"key": "demo-key", "owner": "admin@example.com"}]
