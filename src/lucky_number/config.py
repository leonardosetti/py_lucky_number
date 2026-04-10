"""Configurações oficiais de cada jogo de loteria."""

from enum import Enum
from typing import NamedTuple


class JogoConfig(NamedTuple):
    nome: str
    total_dezenas: int
    min_dezenas: int
    max_dezenas: int
    api_endpoint: str


class Jogo(str, Enum):
    MEGA_SENA = "megasena"
    LOTOFACIL = "lotofacil"
    QUINA = "quina"
    DUPLA_SENA = "duplasena"
    FEDERAL = "federal"
    DIA_DE_SORTE = "diadesorte"


CAIXA_API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api"

JOGOS: dict[Jogo, JogoConfig] = {
    Jogo.MEGA_SENA: JogoConfig(
        nome="Mega-Sena",
        total_dezenas=60,
        min_dezenas=6,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/megasena",
    ),
    Jogo.LOTOFACIL: JogoConfig(
        nome="Lotofácil",
        total_dezenas=25,
        min_dezenas=15,
        max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/lotofacil",
    ),
    Jogo.QUINA: JogoConfig(
        nome="Quina",
        total_dezenas=80,
        min_dezenas=6,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/quina",
    ),
    Jogo.DUPLA_SENA: JogoConfig(
        nome="Dupla Sena",
        total_dezenas=50,
        min_dezenas=6,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/duplasena",
    ),
    Jogo.FEDERAL: JogoConfig(
        nome="Federal",
        total_dezenas=100000,
        min_dezenas=1,
        max_dezenas=5,
        api_endpoint=f"{CAIXA_API_BASE}/federal",
    ),
    Jogo.DIA_DE_SORTE: JogoConfig(
        nome="Dia de Sorte",
        total_dezenas=31,
        min_dezenas=7,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/diadesorte",
    ),
}

MINIMO_INEGOCIAVEL = 6
