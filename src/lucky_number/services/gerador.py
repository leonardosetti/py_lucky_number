"""Gerador de combinações únicas nunca sorteadas."""

import logging
import math
import random
from typing import Optional

from lucky_number.config import JOGOS, Jogo, MINIMO_INEGOCIAVEL
from lucky_number.models import ApostaRequest, ApostaResponse
from lucky_number.services.cache import Cache
from lucky_number.services.caixa_api import CaixaAPIClient

logger = logging.getLogger(__name__)


class EspacoAmostralEsgotadoError(Exception):
    """Lançado quando todas as combinações possíveis já foram sorteadas."""


class GeradorDeApostas:
    def __init__(
        self,
        cache: Optional[Cache] = None,
        caixa_api: Optional[CaixaAPIClient] = None,
    ):
        self.cache = cache or Cache()
        self.caixa_api = caixa_api or CaixaAPIClient()

    async def gerar(
        self,
        jogo: Jogo,
        quantidade_apostas: int,
        dezenas_por_aposta: int,
    ) -> ApostaResponse:
        """Gera combinações únicas nunca sorteadas.

        Algoritmo:
        1. Valida dezenas_por_aposta >= MINIMO_INEGOCIAVEL (6)
        2. Carrega histórico do cache (busca da API se necessário)
        3. Calcula espaço amostral e verifica viabilidade
        4. Gera combinações aleatórias com random.sample()
        5. Filtra contra histórico e contra já-geradas neste batch
        6. Retorna lista ordenada de combinações
        """
        config = JOGOS[jogo]

        if dezenas_por_aposta < MINIMO_INEGOCIAVEL:
            raise ValueError(
                f"Mínimo de {MINIMO_INEGOCIAVEL} dezenas é inegociável"
            )

        historico = await self._garantir_historico(jogo)

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

        return ApostaResponse(
            jogo=jogo.value,
            nome_jogo=config.nome,
            dezenas_por_aposta=dezenas_por_aposta,
            apostas=combinacoes,
        )

    async def gerar_de_request(self, request: ApostaRequest) -> ApostaResponse:
        """Gera apostas a partir de um ApostaRequest."""
        return await self.gerar(
            jogo=request.jogo,
            quantidade_apostas=request.quantidade_apostas,
            dezenas_por_aposta=request.dezenas_por_aposta,
        )

    async def _garantir_historico(self, jogo: Jogo) -> set[tuple[int, ...]]:
        """Garante que o histórico está em cache."""
        historico = self.cache.get(jogo)
        if historico is None:
            historico = await self.caixa_api.buscar_todos_resultados(jogo)
            self.cache.set(jogo, historico)
        return historico

    def _gerar_combinacao(self, total: int, quantidade: int) -> tuple[int, ...]:
        """Gera uma única combinação ordenada."""
        numeros = random.sample(range(1, total + 1), quantidade)
        return tuple(sorted(numeros))

    def _calcular_combinacoes(self, n: int, k: int) -> int:
        """Calcula C(n,k) = n! / (k! * (n-k)!)."""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        return math.comb(n, k)
