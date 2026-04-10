"""Cache em memória singleton para resultados históricos."""

from typing import Optional

from lucky_number.config import Jogo


class Cache:
    """Singleton de cache em memória para resultados históricos."""

    _instance: Optional["Cache"] = None
    _data: dict[Jogo, set[tuple[int, ...]]]

    def __new__(cls) -> "Cache":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
        return cls._instance

    def get(self, jogo: Jogo) -> Optional[set[tuple[int, ...]]]:
        """Retorna combinações já sorteadas ou None se não cacheado."""
        return self._data.get(jogo)

    def set(self, jogo: Jogo, combinacoes: set[tuple[int, ...]]) -> None:
        """Armazena combinações sorteadas."""
        self._data[jogo] = combinacoes

    def invalidate(self, jogo: Optional[Jogo] = None) -> None:
        """Invalida cache de um jogo ou todos."""
        if jogo is None:
            self._data.clear()
        elif jogo in self._data:
            del self._data[jogo]

    def is_cached(self, jogo: Jogo) -> bool:
        """Verifica se jogo está em cache."""
        return jogo in self._data

    def size(self, jogo: Optional[Jogo] = None) -> int:
        """Retorna tamanho do cache."""
        if jogo is None:
            return sum(len(v) for v in self._data.values())
        return len(self._data.get(jogo, set()))

    @classmethod
    def reset(cls) -> None:
        """Reseta o singleton (para testes)."""
        cls._instance = None
