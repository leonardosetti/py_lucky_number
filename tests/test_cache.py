"""Testes para cache em memória."""

import pytest

from lucky_number.config import Jogo
from lucky_number.services.cache import Cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Reseta o cache antes de cada teste."""
    Cache.reset()
    yield
    Cache.reset()


class TestCache:
    """Testes para Cache singleton."""

    def test_get_cache_vazio(self):
        """Cache vazio deve retornar None."""
        cache = Cache()
        assert cache.get(Jogo.MEGA_SENA) is None

    def test_set_e_get(self):
        """Deve armazenar e recuperar dados."""
        cache = Cache()
        combinacoes = {(1, 2, 3, 4, 5, 6), (7, 8, 9, 10, 11, 12)}
        cache.set(Jogo.MEGA_SENA, combinacoes)

        result = cache.get(Jogo.MEGA_SENA)
        assert result == combinacoes
        assert len(result) == 2

    def test_is_cached(self):
        """is_cached deve retornar corretamente."""
        cache = Cache()
        assert not cache.is_cached(Jogo.MEGA_SENA)

        cache.set(Jogo.MEGA_SENA, {(1, 2, 3, 4, 5, 6)})
        assert cache.is_cached(Jogo.MEGA_SENA)
        assert not cache.is_cached(Jogo.LOTOFACIL)

    def test_invalidate_jogo(self):
        """invalidate deve remover dados de um jogo."""
        cache = Cache()
        cache.set(Jogo.MEGA_SENA, {(1, 2, 3, 4, 5, 6)})
        cache.set(Jogo.QUINA, {(1, 2, 3, 4, 5, 6)})

        cache.invalidate(Jogo.MEGA_SENA)

        assert not cache.is_cached(Jogo.MEGA_SENA)
        assert cache.is_cached(Jogo.QUINA)

    def test_invalidate_todos(self):
        """invalidate(None) deve limpar todo cache."""
        cache = Cache()
        cache.set(Jogo.MEGA_SENA, {(1, 2, 3, 4, 5, 6)})
        cache.set(Jogo.QUINA, {(1, 2, 3, 4, 5, 6)})

        cache.invalidate()

        assert not cache.is_cached(Jogo.MEGA_SENA)
        assert not cache.is_cached(Jogo.QUINA)

    def test_singleton(self):
        """Cache deve ser singleton."""
        cache1 = Cache()
        cache2 = Cache()
        assert cache1 is cache2
        assert cache1._data is cache2._data

    def test_size(self):
        """size deve retornar quantidade correta."""
        cache = Cache()
        assert cache.size() == 0

        cache.set(Jogo.MEGA_SENA, {(1, 2, 3, 4, 5, 6), (7, 8, 9, 10, 11, 12)})
        assert cache.size(Jogo.MEGA_SENA) == 2
        assert cache.size(Jogo.QUINA) == 0
        assert cache.size() == 2

    def test_dados_separados_por_jogo(self):
        """Cada jogo deve ter dados independentes."""
        cache = Cache()

        megasena = {(1, 2, 3, 4, 5, 6)}
        quina = {(10, 20, 30, 40, 50, 60)}

        cache.set(Jogo.MEGA_SENA, megasena)
        cache.set(Jogo.QUINA, quina)

        assert cache.get(Jogo.MEGA_SENA) == megasena
        assert cache.get(Jogo.QUINA) == quina
        assert len(cache.get(Jogo.MEGA_SENA)) == 1
        assert len(cache.get(Jogo.QUINA)) == 1
