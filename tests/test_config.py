"""Testes para configurações dos jogos."""

from lucky_number.config import (
    CAIXA_API_BASE,
    JOGOS,
    MINIMO_INEGOCIAVEL,
    Jogo,
    JogoConfig,
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
        """Mínimo deve ser >= 5 para todos (exceto Federal)."""
        for jogo, config in JOGOS.items():
            if jogo != Jogo.FEDERAL:
                assert config.min_dezenas >= 5, (
                    f"{jogo.value}: min_dezenas {config.min_dezenas} < 5"
                )

    def test_max_dezenas_nao_excede_total(self):
        """Max dezenas não pode exceder total de dezenas."""
        for jogo, config in JOGOS.items():
            assert config.max_dezenas <= config.total_dezenas, (
                f"{jogo.value}: max_dezenas {config.max_dezenas} > "
                f"total {config.total_dezenas}"
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
        assert config.max_dezenas == 20

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
        assert config.min_dezenas == 5

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


class TestPrecificacao:
    """Testes para cálculo de preço das apostas."""

    def test_mega_sena_preco_base(self):
        """Preço base Mega-Sena é R$ 6,00."""
        config = JOGOS[Jogo.MEGA_SENA]
        assert config.preco_base == 6.00
        assert config.dezenas_base == 6

    def test_mega_sena_preco_6_dezenas(self):
        """Mega-Sena com 6 dezenas = R$ 6,00."""
        assert JOGOS[Jogo.MEGA_SENA].calcular_preco(6) == 6.00

    def test_mega_sena_preco_7_dezenas(self):
        """Mega-Sena com 7 dezenas = 6.00 * C(7,6) = 6.00 * 7 = R$ 42,00."""
        assert JOGOS[Jogo.MEGA_SENA].calcular_preco(7) == 42.00

    def test_mega_sena_preco_8_dezenas(self):
        """Mega-Sena com 8 dezenas = 6.00 * C(8,6) = 6.00 * 28 = R$ 168,00."""
        assert JOGOS[Jogo.MEGA_SENA].calcular_preco(8) == 168.00

    def test_lotofacil_preco_base(self):
        """Preço base Lotofácil é R$ 3,50."""
        config = JOGOS[Jogo.LOTOFACIL]
        assert config.preco_base == 3.50
        assert config.dezenas_base == 15

    def test_lotofacil_preco_15_dezenas(self):
        """Lotofácil com 15 dezenas = R$ 3,50."""
        assert JOGOS[Jogo.LOTOFACIL].calcular_preco(15) == 3.50

    def test_lotofacil_preco_16_dezenas(self):
        """Lotofácil com 16 dezenas = 3.50 * C(16,15) = 3.50 * 16 = R$ 56,00."""
        assert JOGOS[Jogo.LOTOFACIL].calcular_preco(16) == 56.00

    def test_quina_preco_base(self):
        """Preço base Quina é R$ 3,00."""
        assert JOGOS[Jogo.QUINA].preco_base == 3.00
        assert JOGOS[Jogo.QUINA].dezenas_base == 5

    def test_dupla_sena_preco_base(self):
        """Preço base Dupla Sena é R$ 3,00."""
        assert JOGOS[Jogo.DUPLA_SENA].preco_base == 3.00

    def test_dia_de_sorte_preco_base(self):
        """Preço base Dia de Sorte é R$ 2,00."""
        assert JOGOS[Jogo.DIA_DE_SORTE].preco_base == 2.00

    def test_federal_preco_base(self):
        """Preço base Federal é R$ 4,50."""
        assert JOGOS[Jogo.FEDERAL].preco_base == 4.50
