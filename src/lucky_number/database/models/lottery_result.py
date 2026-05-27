"""Lottery result table registry and DatabaseHistoryProvider.

The 10 loterias_resultados_{jogo} tables use CEF spreadsheet column names
(spaces, accents) so they are created via raw SQL in migration 003 and
accessed via SQLAlchemy Core (text) rather than ORM models.

This module provides:
- TABLE_NAMES: mapping Jogo -> table name
- game_table(): returns table name for a Jogo
- DatabaseHistoryProvider: queries drawn combinations for the generator
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucky_number.config import Jogo
from lucky_number.services.gerador import HistoryProvider

logger = logging.getLogger(__name__)

TABLE_NAMES: dict[Jogo, str] = {
    Jogo.MEGA_SENA: "loterias_resultados_megasena",
    Jogo.LOTOFACIL: "loterias_resultados_lotofacil",
    Jogo.QUINA: "loterias_resultados_quina",
    Jogo.DUPLA_SENA: "loterias_resultados_duplasena",
    Jogo.FEDERAL: "loterias_resultados_federal",
    Jogo.DIA_DE_SORTE: "loterias_resultados_diadesorte",
    Jogo.LOTOMANIA: "loterias_resultados_lotomania",
    Jogo.TIMEMANIA: "loterias_resultados_timemania",
    Jogo.MAIS_MILIONARIA: "loterias_resultados_maismilionaria",
    Jogo.SUPER_SETE: "loterias_resultados_supersete",
    Jogo.LOTECA: "loterias_resultados_loteca",
}


def game_table(jogo: Jogo) -> str:
    return TABLE_NAMES[jogo]


class DatabaseHistoryProvider(HistoryProvider):
    """Queries drawn combinations from the lottery results tables.

    Uses SQLAlchemy Core (text) because the tables have non-standard
    column names with spaces and accented characters.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_drawn_combinations(self, jogo: Jogo) -> set[tuple[int, ...]]:
        table = game_table(jogo)

        if jogo == Jogo.FEDERAL:
            return set()

        if jogo in (Jogo.SUPER_SETE, Jogo.LOTECA):
            return set()

        try:
            result = await self._session.execute(
                text(f"SELECT dezenas_ordenadas FROM {table}")
            )
            rows = result.all()
            drawn: set[tuple[int, ...]] = set()
            for row in rows:
                drawn.add(tuple(row[0]))
            logger.info(f"{jogo.value}: {len(drawn)} drawn combinations loaded")
            return drawn
        except Exception:
            logger.warning(
                f"Could not load drawn combinations for {jogo.value}", exc_info=True
            )
            return set()
