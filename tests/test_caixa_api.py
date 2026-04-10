"""Testes para cliente da API da Caixa."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from lucky_number.config import Jogo
from lucky_number.services.caixa_api import (
    CaixaAPIClient,
    CaixaAPIError,
    TimeoutError,
    NotFoundError,
)


@pytest.fixture
def client():
    """Cliente para testes."""
    return CaixaAPIClient(timeout=5.0, max_retries=2, backoff_base=0.1)


class TestCaixaAPIClient:
    """Testes para CaixaAPIClient."""

    @pytest.mark.asyncio
    async def test_parse_dezenas_megasena(self, client):
        """Deve extrair dezenas corretamente de Mega-Sena."""
        data = {
            "numero": 1234,
            "listaDezenas": ["05", "10", "23", "42", "51", "60"]
        }
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == [5, 10, 23, 42, 51, 60]

    @pytest.mark.asyncio
    async def test_parse_dezenas_lotofacil(self, client):
        """Deve extrair dezenas corretamente de Lotofácil."""
        data = {
            "numero": 1234,
            "listaDezenas": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", 
                           "11", "12", "13", "14", "15"]
        }
        dezenas = client._parse_dezenas(data, Jogo.LOTOFACIL)
        assert dezenas == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    @pytest.mark.asyncio
    async def test_parse_dezenas_federal(self, client):
        """Deve extrair número corretamente de Federal."""
        data = {
            "numero": 1234,
            "listaDezenas": ["12345"]
        }
        dezenas = client._parse_dezenas(data, Jogo.FEDERAL)
        assert dezenas == [12345]

    @pytest.mark.asyncio
    async def test_parse_dezenas_com_zeros(self, client):
        """Deve tratar dezenas com zeros à esquerda."""
        data = {
            "numero": 1234,
            "listaDezenas": ["01", "04", "05", "09", "10", "11"]
        }
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == [1, 4, 5, 9, 10, 11]

    @pytest.mark.asyncio
    async def test_parse_dezenas_vazio(self, client):
        """Deve retornar lista vazia quando não há dezenas."""
        data = {"numero": 1234, "listaDezenas": []}
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == []

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_sucesso(self, client):
        """Deve buscar último concurso com sucesso."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"numero": 1234}
        
        with patch.object(httpx.AsyncClient, '__aenter__', return_value=AsyncMock()) as mock_ctx:
            mock_ctx.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            with patch('lucky_number.services.caixa_api.httpx.AsyncClient') as MockClient:
                instance = AsyncMock()
                instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                MockClient.return_value = instance
                
                result = await client._buscar_ultimo_concurso("https://example.com")
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_timeout(self, client):
        """Deve lançar TimeoutError em timeout."""
        with patch('lucky_number.services.caixa_api.httpx.AsyncClient') as MockClient:
            instance = AsyncMock()
            instance.__aenter__.side_effect = httpx.TimeoutException("Timeout")
            MockClient.return_value = instance
            
            with pytest.raises(TimeoutError):
                await client._buscar_ultimo_concurso("https://example.com")


class TestCaixaAPIExceptions:
    """Testes para exceções da API."""

    def test_timeout_error_heranca(self):
        """TimeoutError deve herdar de CaixaAPIError."""
        assert issubclass(TimeoutError, CaixaAPIError)

    def test_not_found_error_heranca(self):
        """NotFoundError deve herdar de CaixaAPIError."""
        assert issubclass(NotFoundError, CaixaAPIError)
