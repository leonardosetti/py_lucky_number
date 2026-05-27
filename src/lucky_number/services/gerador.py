"""Gerador de combinações únicas nunca sorteadas.

Core business logic (Principles I + III). Gera combinações aleatórias
filtrando contra histórico de sorteios e histórico do próprio usuário.
Prevents CWE-338: uses secrets.SystemRandom for cryptographic security.
"""

import logging
import math
import secrets

from lucky_number.config import JOGOS, MINIMO_POR_JOGO, Jogo
from lucky_number.models import ApostaRequest, ApostaResponse

logger = logging.getLogger(__name__)

_rng = secrets.SystemRandom()


class EspacoAmostralEsgotadoError(Exception):
    """Lançado quando todas as combinações possíveis já foram sorteadas."""


class HistoryProvider:
    """Interface para consulta de histórico de combinações.

    Permite que o GeradorDeApostas consulte combinações já sorteadas
    de forma agnóstica à fonte de dados (cache, banco, API).
    """

    async def get_drawn_combinations(self, jogo: Jogo) -> set[tuple[int, ...]]:
        """Retorna conjunto de combinações já sorteadas para um jogo."""
        return set()


class GeradorDeApostas:
    def __init__(self, history_provider: HistoryProvider | None = None):
        self.history_provider = history_provider or HistoryProvider()

    async def gerar(
        self,
        jogo: Jogo,
        quantidade_apostas: int,
        dezenas_por_aposta: int,
    ) -> ApostaResponse:
        """Gera combinações únicas nunca sorteadas.

        Uses secrets.SystemRandom for cryptographically secure generation.
        """
        config = JOGOS[jogo]
        min_dezenas = MINIMO_POR_JOGO.get(jogo, 6)

        if dezenas_por_aposta < config.min_dezenas:
            raise ValueError(
                f"Mínimo de {config.min_dezenas} dezenas para {config.nome}"
            )
        if dezenas_por_aposta < min_dezenas:
            raise ValueError(
                f"Mínimo inegociável de {min_dezenas} dezenas para {config.nome}"
            )
        if dezenas_por_aposta > config.max_dezenas:
            raise ValueError(
                f"Máximo de {config.max_dezenas} dezenas para {config.nome}"
            )

        historico = await self.history_provider.get_drawn_combinations(jogo)

        espaco_amostral = self._calcular_combinacoes(
            config.total_dezenas, dezenas_por_aposta
        )
        disponiveis = espaco_amostral - len(historico)

        logger.info(
            f"{config.nome}: espaço={espaco_amostral}, "
            f"sorteadas={len(historico)}, disponíveis={disponiveis}"
        )

        if disponiveis < quantidade_apostas:
            raise EspacoAmostralEsgotadoError(
                f"Apenas {disponiveis} combinações disponíveis, "
                f"mas foram solicitadas {quantidade_apostas}"
            )

        geradas: set[tuple[int, ...]] = set()
        combinacoes: list[list[int]] = []
        tentativas = 0
        max_tentativas = quantidade_apostas * 100

        while len(combinacoes) < quantidade_apostas and tentativas < max_tentativas:
            tentativas += 1
            combinacao = self._gerar_combinacao(
                config.total_dezenas, dezenas_por_aposta
            )

            if combinacao not in historico and combinacao not in geradas:
                geradas.add(combinacao)
                combinacoes.append(list(combinacao))

        if len(combinacoes) < quantidade_apostas:
            raise EspacoAmostralEsgotadoError(
                f"Não foi possível gerar {quantidade_apostas} combinações "
                f"após {max_tentativas} tentativas"
            )

        valor_unitario = config.calcular_preco(dezenas_por_aposta)
        return ApostaResponse(
            jogo=jogo.value,
            nome_jogo=config.nome,
            dezenas_por_aposta=dezenas_por_aposta,
            apostas=combinacoes,
            valor_total=round(valor_unitario * quantidade_apostas, 2),
        )

    async def gerar_de_request(self, request: ApostaRequest) -> ApostaResponse:
        """Gera apostas a partir de um ApostaRequest."""
        return await self.gerar(
            jogo=request.jogo,
            quantidade_apostas=request.quantidade_apostas,
            dezenas_por_aposta=request.dezenas_por_aposta,
        )

    def _gerar_combinacao(self, total: int, quantidade: int) -> tuple[int, ...]:
        """Gera uma única combinação ordenada usando secrets.SystemRandom."""
        numeros = _rng.sample(range(1, total + 1), quantidade)
        return tuple(sorted(numeros))

    def _calcular_combinacoes(self, n: int, k: int) -> int:
        """Calcula C(n,k) = n! / (k! * (n-k)!)."""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        return math.comb(n, k)
