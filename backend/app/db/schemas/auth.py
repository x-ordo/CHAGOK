"""
Auth Schemas - Login, Signup, Token, Password Reset
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.db.models import UserRole, UserStatus


# ============================================
# Auth Schemas
# ============================================
class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class SignupRequest(BaseModel):
    """Signup request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    accept_terms: bool = Field(..., description="이용약관 동의 필수")
    role: Optional[UserRole] = Field(
        default=None,
        description="User role (CLIENT, DETECTIVE only for self-signup; LAWYER, STAFF, ADMIN require invitation)"
    )


class UserOut(BaseModel):
    """User output schema (without sensitive data)"""
    id: str
    email: str
    name: str
    role: UserRole
    status: UserStatus
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserOut


# ============================================
# Password Reset Schemas
# ============================================
class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Forgot password response schema"""
    message: str


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str = Field(..., min_length=8)


class ResetPasswordResponse(BaseModel):
    """Reset password response schema"""
    message: str


# ============================================
# User Management Schemas
# ============================================
class UserInviteRequest(BaseModel):
    """User invitation request schema"""
    email: EmailStr
    role: UserRole = Field(default=UserRole.LAWYER)


class InviteResponse(BaseModel):
    """Invite token response schema"""
    invite_token: str
    invite_url: str
    email: str
    role: UserRole
    expires_at: datetime


class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[UserOut]
    total: int


# ============================================
# RBAC / Permission Schemas
# ============================================
class ResourcePermission(BaseModel):
    """Permission for a specific resource"""
    view: bool = False
    edit: bool = False
    delete: bool = False


class RolePermissions(BaseModel):
    """Complete permission set for a role"""
    role: UserRole
    cases: ResourcePermission
    evidence: ResourcePermission
    admin: ResourcePermission
    billing: ResourcePermission


class RolePermissionsResponse(BaseModel):
    """Response schema for GET /admin/roles"""
    roles: list[RolePermissions]


class UpdateRolePermissionsRequest(BaseModel):
    """Request schema for PUT /admin/roles/{role}/permissions"""
    cases: ResourcePermission
    evidence: ResourcePermission
    admin: ResourcePermission
    billing: ResourcePermission
