"""Token-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


class TokenBase(BaseModel):
    """Base token schema."""
    token: str = Field(..., description="The JWT token string")
    token_type: str = Field("bearer", description="The token type, typically 'bearer'")


class Token(TokenBase):
    """Authentication token schema with access token."""
    access_token: str = Field(..., description="The access token string")
    token_type: str = Field("bearer", description="The token type, typically 'bearer'")


class TokenResponse(TokenBase):
    """Token response schema with refresh token."""
    access_token: str = Field(..., description="The access token string")
    refresh_token: str = Field(..., description="The refresh token string")
    token_type: str = Field("bearer", description="The token type, typically 'bearer'")
    expires_in: int = Field(..., description="Time in seconds until the token expires")


class TokenPayload(BaseModel):
    """Payload data stored in the JWT token."""
    sub: Optional[str] = Field(None, description="Subject (user ID)")
    email: Optional[EmailStr] = Field(None, description="User's email")
    scopes: List[str] = Field(default_factory=list, description="List of token scopes")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    iat: Optional[int] = Field(None, description="Issued at timestamp")
    jti: Optional[str] = Field(None, description="JWT ID")


class TokenData(BaseModel):
    """Data extracted from the JWT token."""
    sub: Optional[str] = Field(None, description="Subject (user ID)")
    email: Optional[EmailStr] = Field(None, description="User's email")
    scopes: List[str] = Field(default_factory=list, description="List of token scopes")


class TokenCreate(BaseModel):
    """Schema for token creation."""
    user_id: int = Field(..., description="ID of the user this token belongs to")
    token: str = Field(..., description="The JWT token string")
    expires_at: datetime = Field(..., description="When the token expires")
    revoked: bool = Field(False, description="Whether the token has been revoked")


class TokenUpdate(BaseModel):
    """Schema for token updates."""
    revoked: Optional[bool] = Field(None, description="Whether to revoke the token")


class TokenInDBBase(TokenBase):
    """Base schema for token in database."""
    id: int = Field(..., description="Token ID")
    user_id: int = Field(..., description="ID of the user this token belongs to")
    expires_at: datetime = Field(..., description="When the token expires")
    revoked: bool = Field(..., description="Whether the token has been revoked")
    created_at: datetime = Field(..., description="When the token was created")

    class Config:
        orm_mode = True


class TokenInDB(TokenInDBBase):
    """Schema for token in database."""
    pass


class TokenResponseWithUser(TokenResponse):
    """Token response with user information."""
    user: Dict[str, Any] = Field(..., description="User information")
    """Response schema for token endpoint."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
