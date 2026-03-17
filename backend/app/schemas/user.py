"""
User Schemas
Pydantic models for user data validation.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    picture: Optional[str] = Field(None, max_length=500, description="Profile picture URL")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    google_id: str = Field(..., min_length=1, max_length=255, description="Google user ID")


class UserInDB(UserBase):
    """Schema for user in database (includes all fields)."""

    id: int
    google_id: str
    role: str = "user"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user response (public-facing, no sensitive data)."""

    id: int
    email: EmailStr
    name: str
    picture: Optional[str] = None
    role: str = "user"
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserCreateByAdmin(BaseModel):
    """Schema for creating a user manually (by superadmin), without Google OAuth."""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    role: Literal["user", "admin", "superadmin"] = Field("user", description="User role")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
