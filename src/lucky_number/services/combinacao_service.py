"""Combinacao service — FIFO user combination history (Principle IV)."""

import hashlib
import logging

from sqlalchemy import select, func

from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.combinacao import Combinacao

logger = logging.getLogger(__name__)

MAX_COMBINACOES = 200


async def save_combinacao(
    user_id: str, jogo: str, dezenas: list[int], dezenas_por_aposta: int
) -> Combinacao:
    """Save a combination with FIFO eviction at MAX_COMBINACOES.
    Prevents CWE-89: parameterized queries via SQLAlchemy.
    """
    raw = f"{jogo}:{sorted(dezenas)}:{dezenas_por_aposta}"
    hash_combinacao = hashlib.sha256(raw.encode()).hexdigest()

    async with async_session_factory() as session:
        existing = await session.execute(
            select(Combinacao).where(Combinacao.hash_combinacao == hash_combinacao)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Combinação já existe")

        count = await session.execute(
            select(func.count())
            .select_from(Combinacao)
            .where(Combinacao.user_id == user_id)
        )
        total = count.scalar() or 0

        if total >= MAX_COMBINACOES:
            to_delete = await session.execute(
                select(Combinacao)
                .where(Combinacao.user_id == user_id, not Combinacao.favorita)
                .order_by(Combinacao.created_at.asc())
                .limit(1)
            )
            old = to_delete.scalar_one_or_none()
            if old:
                await session.delete(old)

        combo = Combinacao(
            user_id=user_id,
            jogo=jogo,
            dezenas=sorted(dezenas),
            dezenas_por_aposta=dezenas_por_aposta,
            hash_combinacao=hash_combinacao,
        )
        session.add(combo)
        await session.commit()
        await session.refresh(combo)
        return combo


async def list_combinacoes(
    user_id: str, page: int = 1, per_page: int = 20, jogo: str = None
) -> list[Combinacao]:
    """List user combinations with optional game filter and pagination."""
    async with async_session_factory() as session:
        query = select(Combinacao).where(Combinacao.user_id == user_id)
        if jogo:
            query = query.where(Combinacao.jogo == jogo)
        query = query.order_by(Combinacao.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        return list(result.scalars().all())


async def delete_combinacao(combinacao_id: str, user_id: str) -> bool:
    """Delete a combination by id, ensuring ownership."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Combinacao).where(
                Combinacao.id == combinacao_id, Combinacao.user_id == user_id
            )
        )
        combo = result.scalar_one_or_none()
        if not combo:
            return False
        await session.delete(combo)
        await session.commit()
        return True


async def toggle_favorita(combinacao_id: str, user_id: str) -> bool | None:
    """Toggle favorite status. Returns new state or None if not found."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Combinacao).where(
                Combinacao.id == combinacao_id, Combinacao.user_id == user_id
            )
        )
        combo = result.scalar_one_or_none()
        if not combo:
            return None
        combo.favorita = not combo.favorita
        await session.commit()
        return combo.favorita
