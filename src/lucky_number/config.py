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
    LOTOMANIA = "lotomania"
    TIMEMANIA = "timemania"
    MAIS_MILIONARIA = "maismilionaria"
    SUPER_SETE = "supersete"
    LOTECA = "loteca"


CAIXA_API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api"

JOGOS: dict[Jogo, JogoConfig] = {
    Jogo.MEGA_SENA: JogoConfig(
        nome="Mega-Sena",
        total_dezenas=60, min_dezenas=6, max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/megasena",
        preco_base=6.00, dezenas_base=6,
    ),
    Jogo.LOTOFACIL: JogoConfig(
        nome="Lotofácil",
        total_dezenas=25, min_dezenas=15, max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/lotofacil",
        preco_base=3.50, dezenas_base=15,
    ),
    Jogo.QUINA: JogoConfig(
        nome="Quina",
        total_dezenas=80, min_dezenas=5, max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/quina",
        preco_base=3.00, dezenas_base=5,
    ),
    Jogo.DUPLA_SENA: JogoConfig(
        nome="Dupla Sena",
        total_dezenas=50, min_dezenas=6, max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/duplasena",
        preco_base=3.00, dezenas_base=6,
    ),
    Jogo.FEDERAL: JogoConfig(
        nome="Federal",
        total_dezenas=100000, min_dezenas=1, max_dezenas=5,
        api_endpoint=f"{CAIXA_API_BASE}/federal",
        preco_base=4.50, dezenas_base=1,
    ),
    Jogo.DIA_DE_SORTE: JogoConfig(
        nome="Dia de Sorte",
        total_dezenas=31, min_dezenas=7, max_dezenas=15,
        api_endpoint=f"{CAIXA_API_BASE}/diadesorte",
        preco_base=2.00, dezenas_base=7,
    ),
    Jogo.LOTOMANIA: JogoConfig(
        nome="Lotomania",
        total_dezenas=100, min_dezenas=50, max_dezenas=50,
        api_endpoint=f"{CAIXA_API_BASE}/lotomania",
        preco_base=3.00, dezenas_base=50,
    ),
    Jogo.TIMEMANIA: JogoConfig(
        nome="Timemania",
        total_dezenas=80, min_dezenas=10, max_dezenas=10,
        api_endpoint=f"{CAIXA_API_BASE}/timemania",
        preco_base=3.50, dezenas_base=10,
    ),
    Jogo.MAIS_MILIONARIA: JogoConfig(
        nome="+Milionária",
        total_dezenas=50, min_dezenas=6, max_dezenas=20,
        api_endpoint=f"{CAIXA_API_BASE}/maismilionaria",
        preco_base=6.00, dezenas_base=6,
    ),
    Jogo.SUPER_SETE: JogoConfig(
        nome="Super Sete",
        total_dezenas=7, min_dezenas=1, max_dezenas=7,
        api_endpoint=f"{CAIXA_API_BASE}/supersete",
        preco_base=3.00, dezenas_base=1,
    ),
    Jogo.LOTECA: JogoConfig(
        nome="Loteca",
        total_dezenas=14, min_dezenas=1, max_dezenas=14,
        api_endpoint=f"{CAIXA_API_BASE}/loteca",
        preco_base=4.00, dezenas_base=14,
    ),
}

# Mínimo de dezenas inegociável por jogo (Constitution Principle III)
MINIMO_POR_JOGO: dict[Jogo, int] = {
    Jogo.MEGA_SENA: 6,
    Jogo.LOTOFACIL: 15,
    Jogo.QUINA: 5,
    Jogo.DUPLA_SENA: 6,
    Jogo.FEDERAL: 1,
    Jogo.DIA_DE_SORTE: 7,
    Jogo.LOTOMANIA: 50,
    Jogo.TIMEMANIA: 10,
    Jogo.MAIS_MILIONARIA: 6,
    Jogo.SUPER_SETE: 1,
    Jogo.LOTECA: 1,
}

MINIMO_INEGOCIAVEL = 6  # fallback global
