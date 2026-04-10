"""Testes para rotas da API."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from lucky_number.config import Jogo
from lucky_number.models import ApostaResponse
from lucky_number.services.gerador import EspacoAmostralEsgotadoError


@pytest.fixture
def client():
    """Cliente de teste."""
    from lucky_number.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Testes para endpoint /health."""

    def test_get_health(self, client):
        """Deve retornar status ok."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestJogosDisponiveisEndpoint:
    """Testes para endpoint /jogos-disponiveis."""

    def test_get_jogos_disponiveis(self, client):
        """Deve retornar lista de jogos."""
        response = client.get("/api/v1/jogos-disponiveis")
        assert response.status_code == 200
        data = response.json()
        assert "jogos" in data
        assert len(data["jogos"]) == 6
        
        jogos = {j["jogo"] for j in data["jogos"]}
        assert "megasena" in jogos
        assert "lotofacil" in jogos
        assert "quina" in jogos

    def test_jogo_tem_campos_corretos(self, client):
        """Cada jogo deve ter todos os campos."""
        response = client.get("/api/v1/jogos-disponiveis")
        data = response.json()
        
        for jogo in data["jogos"]:
            assert "jogo" in jogo
            assert "nome" in jogo
            assert "total_dezenas" in jogo
            assert "min_dezenas" in jogo
            assert "max_dezenas" in jogo


class TestGerarApostasEndpoint:
    """Testes para endpoint /gerar-apostas."""

    def test_post_gerar_apostas_validacao_jogo_invalido(self, client):
        """Deve retornar 422 para jogo inválido."""
        response = client.post(
            "/api/v1/gerar-apostas",
            json={
                "jogo": "jogo_inexistente",
                "quantidade_apostas": 5,
                "dezenas_por_aposta": 6,
            },
        )
        assert response.status_code == 422

    def test_post_gerar_apostas_validacao_dezenas_invalidas(self, client):
        """Deve retornar 422 para dezenas inválidas."""
        response = client.post(
            "/api/v1/gerar-apostas",
            json={
                "jogo": "megasena",
                "quantidade_apostas": 5,
                "dezenas_por_aposta": 5,
            },
        )
        assert response.status_code == 422

    def test_post_gerar_apostas_validacao_quantidade_invalida(self, client):
        """Deve retornar 422 para quantidade inválida."""
        response = client.post(
            "/api/v1/gerar-apostas",
            json={
                "jogo": "megasena",
                "quantidade_apostas": 0,
                "dezenas_por_aposta": 6,
            },
        )
        assert response.status_code == 422

    @patch("lucky_number.api.dependencies.get_gerador")
    def test_post_gerar_apostas_sucesso(self, mock_get_gerador, client):
        """Deve retornar 200 com dados válidos."""
        mock_gerador = MagicMock()
        mock_gerador.gerar_de_request = AsyncMock(return_value=ApostaResponse(
            jogo="megasena",
            nome_jogo="Mega-Sena",
            dezenas_por_aposta=6,
            apostas=[[1, 2, 3, 4, 5, 6]],
            timestamp=datetime.now(),
        ))
        mock_get_gerador.return_value = mock_gerador
        
        response = client.post(
            "/api/v1/gerar-apostas",
            json={
                "jogo": "megasena",
                "quantidade_apostas": 1,
                "dezenas_por_aposta": 6,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jogo"] == "megasena"
        assert len(data["apostas"]) == 1

    @patch("lucky_number.api.routes.get_gerador")
    def test_post_gerar_apostas_espaco_esgotado(self, mock_get_gerador, client):
        """Deve retornar 500 quando espaço amostral esgotado."""
        mock_gerador = MagicMock()
        mock_gerador.gerar_de_request = AsyncMock(
            side_effect=EspacoAmostralEsgotadoError("Erro")
        )
        mock_get_gerador.return_value = mock_gerador
        
        response = client.post(
            "/api/v1/gerar-apostas",
            json={
                "jogo": "megasena",
                "quantidade_apostas": 1,
                "dezenas_por_aposta": 6,
            },
        )
        assert response.status_code == 500


class TestIndexEndpoint:
    """Testes para endpoint raiz /."""

    def test_get_index(self, client):
        """Deve servir página ou JSON."""
        response = client.get("/")
        assert response.status_code == 200
