"""Token-related Pydantic schemas."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Authentication token schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload data stored in the JWT token."""
    sub: Optional[str] = None
    scopes: List[str] = []
    exp: Optional[int] = None


class TokenData(BaseModel):
    """Data extracted from the JWT token."""
    email: Optional[EmailStr] = None
    scopes: List[str] = []


class TokenCreate(BaseModel):
    """Schema for token creation."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Response schema for token endpoint."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
