"""Testes para gerador de combinações."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from lucky_number.config import Jogo
from lucky_number.models import ApostaRequest
from lucky_number.services.cache import Cache
from lucky_number.services.gerador import (
    EspacoAmostralEsgotadoError,
    GeradorDeApostas,
)


@pytest.fixture
def mock_cache():
    """Cache mock com histórico vazio."""
    cache = MagicMock(spec=Cache)
    cache.get.return_value = None
    return cache


@pytest.fixture
def mock_api():
    """API mock com histórico vazio."""
    api = MagicMock()
    api.buscar_todos_resultados = AsyncMock(return_value=set())
    return api


@pytest.fixture
def gerador(mock_cache, mock_api):
    """Gerador com dependências mockadas."""
    return GeradorDeApostas(cache=mock_cache, caixa_api=mock_api)


class TestGeradorDeApostas:
    """Testes para GeradorDeApostas."""

    @pytest.mark.asyncio
    async def test_gera_combinacao_tamanho_correto(self, gerador):
        """Combinação deve ter tamanho correto."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=1,
            dezenas_por_aposta=6,
        )
        assert len(result.apostas) == 1
        assert len(result.apostas[0]) == 6

    @pytest.mark.asyncio
    async def test_gera_combinacao_ordenada(self, gerador):
        """Combinação deve estar ordenada."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=1,
            dezenas_por_aposta=6,
        )
        aposta = result.apostas[0]
        assert aposta == sorted(aposta)

    @pytest.mark.asyncio
    async def test_gera_combinacao_dentro_intervalo(self, gerador):
        """Dezenas devem estar dentro do intervalo válido."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=1,
            dezenas_por_aposta=6,
        )
        for dezena in result.apostas[0]:
            assert 1 <= dezena <= 60

    @pytest.mark.asyncio
    async def test_gera_combinacoes_unicas_no_batch(self, gerador):
        """Combinações no mesmo batch devem ser únicas."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=5,
            dezenas_por_aposta=6,
        )
        combinacoes = [tuple(aposta) for aposta in result.apostas]
        assert len(combinacoes) == len(set(combinacoes))

    @pytest.mark.asyncio
    async def test_gera_quantidade_exata(self, gerador):
        """Deve gerar quantidade exata de apostas."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=10,
            dezenas_por_aposta=6,
        )
        assert len(result.apostas) == 10

    @pytest.mark.asyncio
    async def test_respeita_minimo_inegociavel(self, gerador):
        """Deve rejeitar dezenas abaixo do mínimo."""
        with pytest.raises(ValueError) as exc_info:
            await gerador.gerar(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=1,
                dezenas_por_aposta=5,
            )
        assert "inegociável" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_gerar_de_request(self, gerador):
        """gerar_de_request deve funcionar corretamente."""
        request = ApostaRequest(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=3,
            dezenas_por_aposta=6,
        )
        result = await gerador.gerar_de_request(request)
        assert len(result.apostas) == 3
        assert result.jogo == "megasena"

    @pytest.mark.asyncio
    async def test_response_tem_campos_corretos(self, gerador):
        """Response deve ter todos os campos."""
        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=1,
            dezenas_por_aposta=6,
        )
        assert result.jogo == "megasena"
        assert result.nome_jogo == "Mega-Sena"
        assert result.dezenas_por_aposta == 6
        assert result.timestamp is not None


class TestEspacoAmostral:
    """Testes para espaço amostral."""

    @pytest.mark.asyncio
    async def test_calcular_combinacoes(self, gerador):
        """Deve calcular combinações corretamente."""
        assert gerador._calcular_combinacoes(60, 6) == 50063860
        assert gerador._calcular_combinacoes(25, 15) == 3268760
        assert gerador._calcular_combinacoes(6, 6) == 1
        assert gerador._calcular_combinacoes(10, 0) == 1

    @pytest.mark.asyncio
    async def test_espaco_amostral_esgotado(self, mock_cache, mock_api):
        """Deve lançar erro quando espaço amostral esgotado."""
        # Mock scenario: small sample space (10 combinations)
        # with 9 already drawn, leaving only 1 available
        historico_grande = {
            (1, 2, 3, 4, 5, 6),
            (1, 2, 3, 4, 5, 7),
            (1, 2, 3, 4, 5, 8),
            (1, 2, 3, 4, 5, 9),
            (1, 2, 3, 4, 5, 10),
            (1, 2, 3, 4, 6, 7),
            (1, 2, 3, 4, 6, 8),
            (1, 2, 3, 4, 6, 9),
            (1, 2, 3, 4, 6, 10),
        }
        mock_cache.get.return_value = historico_grande

        gerador = GeradorDeApostas(cache=mock_cache, caixa_api=mock_api)

        # Mock _calcular_combinacoes to return small number
        # (10 total, 9 used, 1 available)
        gerador._calcular_combinacoes = lambda n, k: 10

        # Request 2 bets when only 1 is available
        with pytest.raises(EspacoAmostralEsgotadoError):
            await gerador.gerar(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=2,
                dezenas_por_aposta=6,
            )

    @pytest.mark.asyncio
    async def test_nao_gera_combinacao_sorteada(self, mock_cache, mock_api):
        """Não deve gerar combinação já sorteada."""
        sorteadas = {(1, 2, 3, 4, 5, 6)}
        mock_cache.get.return_value = sorteadas

        gerador = GeradorDeApostas(cache=mock_cache, caixa_api=mock_api)

        result = await gerador.gerar(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=10,
            dezenas_por_aposta=6,
        )

        for aposta in result.apostas:
            assert tuple(aposta) not in sorteadas
