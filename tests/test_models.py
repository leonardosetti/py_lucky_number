"""Testes para modelos Pydantic."""

import pytest
from pydantic import ValidationError

from lucky_number.config import Jogo, MINIMO_INEGOCIAVEL
from lucky_number.models import ApostaRequest, ApostaResponse, JogoInfo


class TestApostaRequest:
    """Testes para ApostaRequest."""

    def test_aposta_request_valida(self):
        """Dados válidos devem ser aceitos."""
        request = ApostaRequest(
            jogo=Jogo.MEGA_SENA,
            quantidade_apostas=5,
            dezenas_por_aposta=6,
        )
        assert request.jogo == Jogo.MEGA_SENA
        assert request.quantidade_apostas == 5
        assert request.dezenas_por_aposta == 6

    def test_aposta_request_dezenas_abaixo_minimo(self):
        """Dezenas abaixo do mínimo inegociável (6) deve falhar."""
        with pytest.raises(ValidationError) as exc_info:
            ApostaRequest(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=1,
                dezenas_por_aposta=5,
            )
        assert "inegociável" in str(exc_info.value).lower()

    def test_aposta_request_dezenas_acima_maximo_megasena(self):
        """Dezenas acima do máximo para Mega-Sena (15) deve falhar."""
        with pytest.raises(ValidationError) as exc_info:
            ApostaRequest(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=1,
                dezenas_por_aposta=20,
            )
        assert "máximo" in str(exc_info.value).lower()

    def test_aposta_request_dezenas_acima_total(self):
        """Dezenas acima do total disponível deve falhar."""
        with pytest.raises(ValidationError) as exc_info:
            ApostaRequest(
                jogo=Jogo.LOTOFACIL,
                quantidade_apostas=1,
                dezenas_por_aposta=30,
            )
        assert "máximo" in str(exc_info.value).lower()

    def test_aposta_request_quantidade_zero(self):
        """Quantidade zero deve falhar."""
        with pytest.raises(ValidationError):
            ApostaRequest(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=0,
                dezenas_por_aposta=6,
            )

    def test_aposta_request_quantidade_negativa(self):
        """Quantidade negativa deve falhar."""
        with pytest.raises(ValidationError):
            ApostaRequest(
                jogo=Jogo.MEGA_SENA,
                quantidade_apostas=-1,
                dezenas_por_aposta=6,
            )



class TestApostaResponse:
    """Testes para ApostaResponse."""

    def test_aposta_response_serializacao(self):
        """Response deve serializar corretamente."""
        response = ApostaResponse(
            jogo="megasena",
            nome_jogo="Mega-Sena",
            dezenas_por_aposta=6,
            apostas=[[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]],
        )
        data = response.model_dump()
        assert data["jogo"] == "megasena"
        assert len(data["apostas"]) == 2
        assert data["timestamp"] is not None

    def test_aposta_response_timestamp(self):
        """Timestamp deve ser gerado automaticamente."""
        response = ApostaResponse(
            jogo="megasena",
            nome_jogo="Mega-Sena",
            dezenas_por_aposta=6,
            apostas=[[1, 2, 3, 4, 5, 6]],
        )
        assert response.timestamp is not None


class TestJogoInfo:
    """Testes para JogoInfo."""

    def test_jogo_info_criacao(self):
        """JogoInfo deve criar corretamente."""
        info = JogoInfo(
            jogo="megasena",
            nome="Mega-Sena",
            total_dezenas=60,
            min_dezenas=6,
            max_dezenas=15,
        )
        assert info.jogo == "megasena"
        assert info.nome == "Mega-Sena"
