"""User-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    
    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    current_password: Optional[str] = Field(None, description="Current password for verification")
    new_password: Optional[str] = Field(
        None, 
        min_length=8, 
        description="New password (min 8 characters, requires current_password)"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v: Optional[str], values) -> Optional[str]:
        """Validate new password if provided."""
        if v is not None:
            if 'current_password' not in values or not values['current_password']:
                raise ValueError("Current password is required to set a new password")
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters long")
            if not any(c.isupper() for c in v):
                raise ValueError("Password must contain at least one uppercase letter")
            if not any(c.isdigit() for c in v):
                raise ValueError("Password must contain at least one number")
        return v


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDBBase):
    """User schema for API responses."""
    pass

# Alias for backward compatibility
User = UserResponse


class UserInDB(UserInDBBase):
    """Schema for user in database (includes hashed password)."""
    hashed_password: str


class Token(BaseModel):
    """Authentication token schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[EmailStr] = None
    scopes: List[str] = []


class UserProjectsStats(BaseModel):
    """User projects statistics."""
    total_projects: int = 0
    active_projects: int = 0
    total_searches: int = 0
    domains_tracked: int = 0


class UserProfile(User):
    """Extended user profile with statistics."""
    stats: UserProjectsStats
