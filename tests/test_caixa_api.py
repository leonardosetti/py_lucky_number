"""Testes para cliente da API da Caixa."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from lucky_number.config import Jogo
from lucky_number.services.caixa_api import (
    CaixaAPIClient,
    CaixaAPIError,
    NotFoundError,
    TimeoutError,
)


@pytest.fixture
def client():
    """Cliente para testes."""
    return CaixaAPIClient(timeout=5.0, max_retries=2, backoff_base=0.1)


@pytest.fixture
def mock_response_200():
    """Mock response 200."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "numero": 1234,
        "listaDezenas": ["01", "02", "03", "04", "05", "06"],
    }
    return mock


@pytest.fixture
def mock_response_404():
    """Mock response 404."""
    mock = MagicMock()
    mock.status_code = 404
    return mock


@pytest.fixture
def mock_response_500():
    """Mock response 500."""
    mock = MagicMock()
    mock.status_code = 500
    return mock


class TestCaixaAPIClient:
    """Testes para CaixaAPIClient."""

    @pytest.mark.asyncio
    async def test_parse_dezenas_megasena(self, client):
        """Deve extrair dezenas corretamente de Mega-Sena."""
        data = {"numero": 1234, "listaDezenas": ["05", "10", "23", "42", "51", "60"]}
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == [5, 10, 23, 42, 51, 60]

    @pytest.mark.asyncio
    async def test_parse_dezenas_lotofacil(self, client):
        """Deve extrair dezenas corretamente de Lotofácil."""
        data = {
            "numero": 1234,
            "listaDezenas": [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
            ],
        }
        dezenas = client._parse_dezenas(data, Jogo.LOTOFACIL)
        assert dezenas == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    @pytest.mark.asyncio
    async def test_parse_dezenas_quina(self, client):
        """Deve extrair dezenas corretamente de Quina."""
        data = {"numero": 1234, "listaDezenas": ["05", "15", "25", "35", "45"]}
        dezenas = client._parse_dezenas(data, Jogo.QUINA)
        assert dezenas == [5, 15, 25, 35, 45]

    @pytest.mark.asyncio
    async def test_parse_dezenas_duplasena(self, client):
        """Deve extrair dezenas corretamente de Dupla Sena."""
        data = {"numero": 1234, "listaDezenas": ["01", "10", "20", "30", "40", "50"]}
        dezenas = client._parse_dezenas(data, Jogo.DUPLA_SENA)
        assert dezenas == [1, 10, 20, 30, 40, 50]

    @pytest.mark.asyncio
    async def test_parse_dezenas_diadesorte(self, client):
        """Deve extrair dezenas corretamente de Dia de Sorte."""
        data = {
            "numero": 1234,
            "listaDezenas": ["01", "05", "10", "15", "20", "25", "30"],
        }
        dezenas = client._parse_dezenas(data, Jogo.DIA_DE_SORTE)
        assert dezenas == [1, 5, 10, 15, 20, 25, 30]

    @pytest.mark.asyncio
    async def test_parse_dezenas_federal(self, client):
        """Deve extrair número corretamente de Federal."""
        data = {"numero": 1234, "listaDezenas": ["12345"]}
        dezenas = client._parse_dezenas(data, Jogo.FEDERAL)
        assert dezenas == [12345]

    @pytest.mark.asyncio
    async def test_parse_dezenas_com_zeros(self, client):
        """Deve tratar dezenas com zeros à esquerda."""
        data = {"numero": 1234, "listaDezenas": ["01", "04", "05", "09", "10", "11"]}
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == [1, 4, 5, 9, 10, 11]

    @pytest.mark.asyncio
    async def test_parse_dezenas_vazio(self, client):
        """Deve retornar lista vazia quando não há dezenas."""
        data = {"numero": 1234, "listaDezenas": []}
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == []

    @pytest.mark.asyncio
    async def test_parse_dezenas_inteiros(self, client):
        """Deve tratar dezenas já como inteiros."""
        data = {"numero": 1234, "listaDezenas": [1, 2, 3, 4, 5, 6]}
        dezenas = client._parse_dezenas(data, Jogo.MEGA_SENA)
        assert dezenas == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_sucesso(self, client, mock_response_200):
        """Deve buscar último concurso com sucesso."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response_200
            )
            MockClient.return_value = instance

            result = await client._buscar_ultimo_concurso("https://example.com")

        assert result is not None
        assert result["numero"] == 1234

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_timeout(self, client):
        """Deve lançar TimeoutError em timeout."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.side_effect = httpx.TimeoutException("Timeout")
            MockClient.return_value = instance

            with pytest.raises(TimeoutError):
                await client._buscar_ultimo_concurso("https://example.com")

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_erro_generico(self, client):
        """Deve retornar None em erro genérico."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.side_effect = Exception("Erro generico")
            MockClient.return_value = instance

            result = await client._buscar_ultimo_concurso("https://example.com")
            assert result is None

    @pytest.mark.asyncio
    async def test_buscar_ultimo_concurso_status_nao_200(
        self, client, mock_response_404
    ):
        """Deve retornar None quando status não é 200."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response_404
            )
            MockClient.return_value = instance

            result = await client._buscar_ultimo_concurso("https://example.com")
            assert result is None

    @pytest.mark.asyncio
    async def test_buscar_dezenas_sucesso(self, client, mock_response_200):
        """Deve buscar dezenas com sucesso."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response_200
            )
            MockClient.return_value = instance

            result = await client._buscar_dezenas(
                "https://example.com", 1234, Jogo.MEGA_SENA
            )
            assert result == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_buscar_dezenas_not_found(self, client, mock_response_404):
        """Deve lançar NotFoundError em 404."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response_404
            )
            MockClient.return_value = instance

            with pytest.raises(NotFoundError):
                await client._buscar_dezenas(
                    "https://example.com", 1234, Jogo.MEGA_SENA
                )

    @pytest.mark.asyncio
    async def test_buscar_dezenas_http_error(self, client, mock_response_500):
        """Deve lançar CaixaAPIError em erro HTTP."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response_500
            )
            MockClient.return_value = instance

            with pytest.raises(CaixaAPIError):
                await client._buscar_dezenas(
                    "https://example.com", 1234, Jogo.MEGA_SENA
                )

    @pytest.mark.asyncio
    async def test_buscar_dezenas_timeout_com_retry(self, client):
        """Deve retry em timeout e eventualmente lançar TimeoutError."""
        with patch("lucky_number.services.caixa_api.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.__aenter__.side_effect = httpx.TimeoutException("Timeout")
            MockClient.return_value = instance

            with pytest.raises(TimeoutError):
                await client._buscar_dezenas(
                    "https://example.com", 1234, Jogo.MEGA_SENA
                )

    @pytest.mark.asyncio
    async def test_buscar_todos_resultados_vazio(self, client):
        """Deve retornar set vazio quando não encontra concursos."""
        with patch.object(client, "_buscar_ultimo_concurso", return_value=None):
            result = await client.buscar_todos_resultados(Jogo.MEGA_SENA)
            assert result == set()

    @pytest.mark.asyncio
    async def test_buscar_todos_resultados_pequeno(self, client, mock_response_200):
        """Deve buscar todos os resultados."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Return different combinations for each concurso
            return [
                call_count,
                call_count + 1,
                call_count + 2,
                call_count + 3,
                call_count + 4,
                call_count + 5,
            ]

        with patch.object(
            client, "_buscar_ultimo_concurso", return_value={"numero": 2}
        ):
            with patch.object(client, "_buscar_dezenas", side_effect=side_effect):
                result = await client.buscar_todos_resultados(Jogo.MEGA_SENA)
                assert len(result) == 2
                assert (1, 2, 3, 4, 5, 6) in result
                assert (2, 3, 4, 5, 6, 7) in result

    @pytest.mark.asyncio
    async def test_buscar_todos_resultados_not_found_ignored(self, client):
        """Deve ignorar NotFoundError e continuar."""
        with patch.object(
            client, "_buscar_ultimo_concurso", return_value={"numero": 3}
        ):
            with patch.object(client, "_buscar_dezenas") as mock_buscar:
                mock_buscar.side_effect = [
                    [1, 2, 3, 4, 5, 6],
                    NotFoundError("Not found"),
                    [7, 8, 9, 10, 11, 12],
                ]
                # Simular comportamento: NotFoundError é capturado
                result = await client.buscar_todos_resultados(Jogo.MEGA_SENA)
                # Apenas 2 combinações válidas
                assert len(result) == 2

    @pytest.mark.asyncio
    async def test_buscar_todos_resultados_timeout_ignored(self, client):
        """Deve ignorar TimeoutError e continuar."""
        with patch.object(
            client, "_buscar_ultimo_concurso", return_value={"numero": 2}
        ):
            with patch.object(client, "_buscar_dezenas") as mock_buscar:
                mock_buscar.side_effect = [
                    [1, 2, 3, 4, 5, 6],
                    TimeoutError("Timeout"),
                ]
                result = await client.buscar_todos_resultados(Jogo.MEGA_SENA)
                assert len(result) == 1

    @pytest.mark.asyncio
    async def test_buscar_todos_resultados_para_em_max_erros(self, client):
        """Deve parar após max_errors erros consecutivos."""
        with patch.object(
            client, "_buscar_ultimo_concurso", return_value={"numero": 100}
        ):
            with patch.object(
                client, "_buscar_dezenas", side_effect=NotFoundError("Not found")
            ):
                result = await client.buscar_todos_resultados(Jogo.MEGA_SENA)
                # Deve parar após 50 erros consecutivos
                assert len(result) == 0


class TestCaixaAPIExceptions:
    """Testes para exceções da API."""

    def test_timeout_error_heranca(self):
        """TimeoutError deve herdar de CaixaAPIError."""
        assert issubclass(TimeoutError, CaixaAPIError)

    def test_not_found_error_heranca(self):
        """NotFoundError deve herdar de CaixaAPIError."""
        assert issubclass(NotFoundError, CaixaAPIError)

    def test_caixa_api_error_instanciacao(self):
        """CaixaAPIError pode ser instanciado."""
        err = CaixaAPIError("Test error")
        assert str(err) == "Test error"

    def test_timeout_error_instanciacao(self):
        """TimeoutError pode ser instanciado."""
        err = TimeoutError("Timeout")
        assert str(err) == "Timeout"

    def test_not_found_error_instanciacao(self):
        """NotFoundError pode ser instanciado."""
        err = NotFoundError("Not found")
        assert str(err) == "Not found"
