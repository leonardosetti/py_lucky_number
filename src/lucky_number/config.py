"""Configurações oficiais de cada jogo de loteria."""

import math
from enum import Enum
from typing import NamedTuple


class JogoConfig(NamedTuple):
    nome: str
    total_dezenas: int
    min_dezenas: int
    max_dezenas: int
    api_endpoint: str
    preco_base: float = 0.0
    dezenas_base: int = 0

    def calcular_preco(self, dezenas_por_aposta: int) -> float:
        """Calcula o preço de uma aposta com base no número de dezenas."""
        if self.dezenas_base == 0 or dezenas_por_aposta <= self.dezenas_base:
            return self.preco_base
        combinacoes = math.comb(dezenas_por_aposta, self.dezenas_base)
        return round(self.preco_base * combinacoes, 2)


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
        max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/megasena",
        preco_base=6.00,
        dezenas_base=6,
    ),
    Jogo.LOTOFACIL: JogoConfig(
        nome="Lotofácil",
        total_dezenas=25,
        min_dezenas=15,
        max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/lotofacil",
        preco_base=3.50,
        dezenas_base=15,
    ),
    Jogo.QUINA: JogoConfig(
        nome="Quina",
        total_dezenas=80,
        min_dezenas=5,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/quina",
        preco_base=3.00,
        dezenas_base=5,
    ),
    Jogo.DUPLA_SENA: JogoConfig(
        nome="Dupla Sena",
        total_dezenas=50,
        min_dezenas=6,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/duplasena",
        preco_base=3.00,
        dezenas_base=6,
    ),
    Jogo.FEDERAL: JogoConfig(
        nome="Federal",
        total_dezenas=100000,
        min_dezenas=1,
        max_dezenas=5,
        api_endpoint=f"{CAIXA_API_BASE}/federal",
        preco_base=4.50,
        dezenas_base=1,
    ),
    Jogo.DIA_DE_SORTE: JogoConfig(
        nome="Dia de Sorte",
        total_dezenas=31,
        min_dezenas=7,
        max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/diadesorte",
        preco_base=2.00,
        dezenas_base=7,
    ),
}

MINIMO_INEGOCIAVEL = 6
