"""Dependencies do FastAPI."""

from functools import lru_cache

from lucky_number.services.cache import Cache
from lucky_number.services.caixa_api import CaixaAPIClient
from lucky_number.services.gerador import GeradorDeApostas


@lru_cache
def get_cache() -> Cache:
    """Retorna instância singleton do Cache."""
    return Cache()


@lru_cache
def get_caixa_api() -> CaixaAPIClient:
    """Retorna instância do cliente da API Caixa."""
    return CaixaAPIClient()


@lru_cache
def get_gerador() -> GeradorDeApostas:
    """Retorna instância do GeradorDeApostas."""
    return GeradorDeApostas(
        cache=get_cache(),
        caixa_api=get_caixa_api(),
    )
