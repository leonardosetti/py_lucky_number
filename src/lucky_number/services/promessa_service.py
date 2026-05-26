"""Promessa service — Bet promise simulation (Principle V)."""
import hashlib
import logging
import secrets

from sqlalchemy import select, func

from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.promessa import Promessa

logger = logging.getLogger(__name__)

MAX_PROMESSAS = 50
SHARING_TTL_DAYS = 7


async def create_promessa(
    user_id: str, titulo: str | None, prioridade: str, valor_total: float,
    combinacoes: list[dict],
) -> Promessa:
    """Create a bet promise with FIFO eviction at MAX_PROMESSAS."""
    async with async_session_factory() as session:
        count = await session.execute(
            select(func.count()).select_from(Promessa).where(Promessa.user_id == user_id)
        )
        total = count.scalar() or 0

        if total >= MAX_PROMESSAS:
            to_delete = await session.execute(
                select(Promessa)
                .where(Promessa.user_id == user_id, not Promessa.favorita)
                .order_by(Promessa.created_at.asc())
                .limit(1)
            )
            old = to_delete.scalar_one_or_none()
            if old:
                await session.delete(old)

        promessa = Promessa(
            user_id=user_id,
            titulo=titulo,
            prioridade=prioridade,
            valor_total=valor_total,
            combinacoes_snapshot=combinacoes if combinacoes else None,
        )
        session.add(promessa)
        await session.commit()
        await session.refresh(promessa)
        return promessa


async def list_promessas(user_id: str, page: int = 1, per_page: int = 20, prioridade: str = None) -> list[Promessa]:
    """List user promises with optional priority filter."""
    async with async_session_factory() as session:
        query = select(Promessa).where(Promessa.user_id == user_id)
        if prioridade:
            query = query.where(Promessa.prioridade == prioridade)
        query = query.order_by(Promessa.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        return list(result.scalars().all())


async def delete_promessa(promessa_id: str, user_id: str) -> bool:
    """Delete a promise by id, ensuring ownership."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Promessa).where(Promessa.id == promessa_id, Promessa.user_id == user_id)
        )
        promessa = result.scalar_one_or_none()
        if not promessa:
            return False
        await session.delete(promessa)
        await session.commit()
        return True


async def clone_promessa(promessa_id: str, user_id: str) -> Promessa | None:
    """Clone a promise."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Promessa).where(Promessa.id == promessa_id, Promessa.user_id == user_id)
        )
        original = result.scalar_one_or_none()
        if not original:
            return None
        clone = Promessa(
            user_id=user_id,
            titulo=f"{original.titulo or 'Promessa'} (cópia)",
            prioridade=original.prioridade,
            valor_total=original.valor_total,
            combinacoes_snapshot=original.combinacoes_snapshot,
        )
        session.add(clone)
        await session.commit()
        await session.refresh(clone)
        return clone


async def share_promessa(promessa_id: str, user_id: str) -> str | None:
    """Generate HMAC sharing hash for a promise (7-day expiry)."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Promessa).where(Promessa.id == promessa_id, Promessa.user_id == user_id)
        )
        promessa = result.scalar_one_or_none()
        if not promessa:
            return None
        share_hash = hashlib.sha256(
            f"{promessa.id}:{secrets.token_hex(16)}".encode()
        ).hexdigest()[:32]
        promessa.hash_compartilhamento = share_hash
        await session.commit()
        return share_hash
