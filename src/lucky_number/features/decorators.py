"""Feature toggle decorator for route protection."""

from functools import wraps
from fastapi import HTTPException, status

from lucky_number.features.registry import FeatureRegistry

registry = FeatureRegistry()


def require_feature(slug: str):
    """Decorator that returns 404 if the specified feature is inactive.

    Usage:
        @router.get("/endpoint")
        @require_feature("geracao-apostas")
        async def my_endpoint():
            ...

    Prevents CWE-284: Improper Access Control by checking feature activation.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not await registry.is_active(slug):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Feature '{slug}' está indisponível",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
