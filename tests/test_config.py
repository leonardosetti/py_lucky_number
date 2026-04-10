"""Testes para configurações dos jogos."""

import pytest

from lucky_number.config import (
    JOGOS,
    Jogo,
    JogoConfig,
    MINIMO_INEGOCIAVEL,
    CAIXA_API_BASE,
)


class TestJogoEnum:
    """Testes para enum Jogo."""

    def test_todos_jogos_definidos(self):
        """Todos os 6 jogos devem estar definidos."""
        assert len(Jogo) == 6
        assert Jogo.MEGA_SENA.value == "megasena"
        assert Jogo.LOTOFACIL.value == "lotofacil"
        assert Jogo.QUINA.value == "quina"
        assert Jogo.DUPLA_SENA.value == "duplasena"
        assert Jogo.FEDERAL.value == "federal"
        assert Jogo.DIA_DE_SORTE.value == "diadesorte"


class TestJogoConfig:
    """Testes para JogoConfig."""

    def test_todos_jogos_tem_config(self):
        """Todos os jogos devem ter configuração."""
        assert len(JOGOS) == 6
        for jogo in Jogo:
            assert jogo in JOGOS
            config = JOGOS[jogo]
            assert isinstance(config, JogoConfig)
            assert config.nome
            assert config.total_dezenas > 0
            assert config.min_dezenas > 0
            assert config.max_dezenas >= config.min_dezenas

    def test_min_dezenas_respeita_inegociavel(self):
        """Mínimo deve ser >= 6 para todos (exceto Federal)."""
        for jogo, config in JOGOS.items():
            if jogo != Jogo.FEDERAL:
                assert config.min_dezenas >= MINIMO_INEGOCIAVEL, (
                    f"{jogo.value}: min_dezenas {config.min_dezenas} < {MINIMO_INEGOCIAVEL}"
                )

    def test_max_dezenas_nao_excede_total(self):
        """Max dezenas não pode exceder total de dezenas."""
        for jogo, config in JOGOS.items():
            assert config.max_dezenas <= config.total_dezenas, (
                f"{jogo.value}: max_dezenas {config.max_dezenas} > total {config.total_dezenas}"
            )

    def test_api_endpoints_validos(self):
        """Endpoints da API devem ser URLs válidas."""
        for jogo, config in JOGOS.items():
            assert config.api_endpoint.startswith(CAIXA_API_BASE)
            assert config.api_endpoint.endswith(jogo.value)


class TestConfigValores:
    """Testes para valores específicos."""

    def test_mega_sena(self):
        """Config Mega-Sena."""
        config = JOGOS[Jogo.MEGA_SENA]
        assert config.nome == "Mega-Sena"
        assert config.total_dezenas == 60
        assert config.min_dezenas == 6
        assert config.max_dezenas == 15

    def test_lotofacil(self):
        """Config Lotofácil."""
        config = JOGOS[Jogo.LOTOFACIL]
        assert config.nome == "Lotofácil"
        assert config.total_dezenas == 25
        assert config.min_dezenas == 15
        assert config.max_dezenas == 20

    def test_quina(self):
        """Config Quina."""
        config = JOGOS[Jogo.QUINA]
        assert config.nome == "Quina"
        assert config.total_dezenas == 80
        assert config.min_dezenas == 6

    def test_federal(self):
        """Config Federal."""
        config = JOGOS[Jogo.FEDERAL]
        assert config.nome == "Federal"
        assert config.total_dezenas == 100000
        assert config.min_dezenas == 1
        assert config.max_dezenas == 5

    def test_minimo_inegociavel(self):
        """MINIMO_INEGOCIAVEL deve ser 6."""
        assert MINIMO_INEGOCIAVEL == 6
