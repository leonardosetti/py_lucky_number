"""Testes para rotas da API."""

import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from lucky_number.api.auth import get_current_user
from lucky_number.models import ApostaResponse
from lucky_number.services.gerador import EspacoAmostralEsgotadoError


os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def client():
    """Cliente de teste."""
    from lucky_number.main import app

    # Override auth dependency to bypass JWT for tests
    async def override_get_current_user():
        return {"id": "00000000-0000-0000-0000-000000000001", "email": "admin@test.com", "role": "admin"}

    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)


class TestHealthEndpoint:
    """Testes para endpoint /health."""

    def test_get_health(self, client):
        """Deve retornar status ok (ou degraded sem DB)."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded")
        assert "database" in data
        assert "redis" in data
        assert "timestamp" in data


class TestJogosDisponiveisEndpoint:
    """Testes para endpoint /jogos-disponiveis."""

    def test_get_jogos_disponiveis(self, client):
        """Deve retornar lista de jogos."""
        response = client.get("/api/v1/jogos-disponiveis")
        assert response.status_code == 200
        data = response.json()
        assert "jogos" in data
        assert len(data["jogos"]) == 11

        jogos = {j["jogo"] for j in data["jogos"]}
        assert "megasena" in jogos
        assert "lotofacil" in jogos
        assert "quina" in jogos
        assert "lotomania" in jogos
        assert "timemania" in jogos
        assert "maismilionaria" in jogos
        assert "supersete" in jogos
        assert "loteca" in jogos

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

    def test_post_gerar_apostas_sucesso(self, client):
        """Deve retornar 200 com dados válidos via mock direto."""
        from lucky_number.main import app
        from lucky_number.api.dependencies import get_gerador

        mock_gerador = MagicMock()
        mock_gerador.gerar_de_request = AsyncMock(
            return_value=ApostaResponse(
                jogo="megasena",
                nome_jogo="Mega-Sena",
                dezenas_por_aposta=6,
                apostas=[[1, 2, 3, 4, 5, 6]],
                valor_total=6.0,
                timestamp=datetime.now(),
            )
        )

        def override_get_gerador():
            return mock_gerador

        app.dependency_overrides[get_gerador] = override_get_gerador

        try:
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
        finally:
            app.dependency_overrides.clear()

    def test_post_gerar_apostas_espaco_esgotado(self, client):
        """Deve retornar 500 quando espaço amostral esgotado."""
        from lucky_number.main import app
        from lucky_number.api.dependencies import get_gerador

        mock_gerador = MagicMock()
        mock_gerador.gerar_de_request = AsyncMock(
            side_effect=EspacoAmostralEsgotadoError("Erro")
        )

        def override_get_gerador():
            return mock_gerador

        app.dependency_overrides[get_gerador] = override_get_gerador

        try:
            response = client.post(
                "/api/v1/gerar-apostas",
                json={
                    "jogo": "megasena",
                    "quantidade_apostas": 1,
                    "dezenas_por_aposta": 6,
                },
            )
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()


class TestIndexEndpoint:
    """Testes para endpoint raiz /."""

    def test_get_index(self, client):
        """Deve redirecionar para o frontend Next.js."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Redirect
