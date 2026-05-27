"""FastAPI dependencies for Lucky Number."""

from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lucky_number.api.auth import get_current_user
from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.lottery_result import DatabaseHistoryProvider
from lucky_number.database.models.permission import Permission
from lucky_number.database.models.role_permission import RolePermission
from lucky_number.services.cache import Cache
from lucky_number.services.gerador import GeradorDeApostas


async def require_permission(slug: str):
    """Dependency that checks RBAC permission via role_permissions table.
    Prevents CWE-284: Improper Access Control.
    """

    async def check_permission(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role", "")
        if role == "admin":
            return current_user
        async with async_session_factory() as session:
            perm_result = await session.execute(
                select(Permission).where(Permission.slug == slug)
            )
            permission = perm_result.scalar_one_or_none()
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão não encontrada: {slug}",
                )
            rp_result = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role,
                    RolePermission.permission_id == permission.id,
                    RolePermission.granted,
                )
            )
            if not rp_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão necessária: {slug}",
                )
        return current_user

    return check_permission


@lru_cache
def get_cache() -> Cache:
    return Cache()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields a database session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_gerador(
    session: AsyncSession = Depends(get_db_session),
) -> GeradorDeApostas:
    """Creates GeradorDeApostas with DatabaseHistoryProvider."""
    provider = DatabaseHistoryProvider(session)
    return GeradorDeApostas(history_provider=provider)
