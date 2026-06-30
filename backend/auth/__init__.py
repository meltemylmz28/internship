"""Authentication package for the MVP backend scaffold."""

from .services import AuthService, AuthUser, Role, require_role

__all__ = ["AuthService", "AuthUser", "Role", "require_role"]
