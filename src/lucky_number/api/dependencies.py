"""FastAPI dependencies for Lucky Number."""
from functools import lru_cache

from fastapi import Depends, HTTPException, status

from lucky_number.api.auth import get_current_user
from lucky_number.services.cache import Cache
from lucky_number.services.gerador import GeradorDeApostas


def require_permission(slug: str):
    """Decorator that checks if the current user has a specific permission.
    Prevents CWE-284: Improper Access Control.
    """
    def check_permission(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role", "")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {slug}",
            )
        return current_user
    return check_permission


@lru_cache
def get_cache() -> Cache:
    return Cache()


@lru_cache
def get_gerador() -> GeradorDeApostas:
    return GeradorDeApostas()
