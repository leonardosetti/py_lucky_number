"""Cliente HTTP async para API da Caixa com retry e timeout."""

import asyncio
import logging
from typing import Optional

import httpx

from lucky_number.config import Jogo, JOGOS

logger = logging.getLogger(__name__)


class CaixaAPIError(Exception):
    """Erro ao acessar a API da Caixa."""


class TimeoutError(CaixaAPIError):
    """Timeout ao acessar a API."""


class NotFoundError(CaixaAPIError):
    """Recurso não encontrado na API."""


class CaixaAPIClient:
    """Cliente async para API da Caixa com retry e timeout."""

    def __init__(
        self,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_base: float = 1.0,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base

    async def buscar_todos_resultados(self, jogo: Jogo) -> set[tuple[int, ...]]:
        """Busca TODOS os concursos históricos de um jogo.

        Estratégia:
        1. Busca o último concurso para saber o total
        2. Itera de trás pra frente buscando cada concurso
        3. Extrai dezenas sorteadas
        """
        config = JOGOS[jogo]
        logger.info(f"Buscando histórico para {config.nome}...")

        ultimo = await self._buscar_ultimo_concurso(config.api_endpoint)
        if not ultimo:
            return set()

        total_concursos = ultimo.get("numero", 0)
        logger.info(f"Total de concursos: {total_concursos}")

        combinacoes: set[tuple[int, ...]] = set()
        errors = 0
        max_errors = 50

        for concurso in range(total_concursos, 0, -1):
            if errors >= max_errors:
                logger.warning(f"Parando após {max_errors} erros consecutivos")
                break

            try:
                dezenas = await self._buscar_dezenas(
                    config.api_endpoint, concurso, jogo
                )
                if dezenas:
                    combinacoes.add(tuple(sorted(dezenas)))
                    errors = 0
            except NotFoundError:
                errors += 1
            except TimeoutError:
                errors += 1
                await asyncio.sleep(self.backoff_base * 2)
            except Exception as e:
                logger.debug(f"Erro no concurso {concurso}: {e}")
                errors += 1

        logger.info(f"Encontradas {len(combinacoes)} combinações para {config.nome}")
        return combinacoes

    async def _buscar_ultimo_concurso(self, endpoint: str) -> Optional[dict]:
        """Busca o concurso mais recente."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    return response.json()
                return None
        except httpx.TimeoutException:
            raise TimeoutError(f"Timeout ao buscar {endpoint}")
        except Exception as e:
            logger.error(f"Erro ao buscar último concurso: {e}")
            return None

    async def _buscar_dezenas(
        self, endpoint: str, concurso: int, jogo: Jogo
    ) -> list[int]:
        """Busca as dezenas sorteadas de um concurso específico."""
        url = f"{endpoint}/{concurso}"

        for tentativa in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url)

                    if response.status_code == 404:
                        raise NotFoundError(f"Concurso {concurso} não encontrado")

                    if response.status_code != 200:
                        raise CaixaAPIError(
                            f"HTTP {response.status_code} para {url}"
                        )

                    data = response.json()
                    return self._parse_dezenas(data, jogo)

            except httpx.TimeoutException:
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(self.backoff_base * (2**tentativa))
                    continue
                raise TimeoutError(f"Timeout após {self.max_retries} tentativas")

    def _parse_dezenas(self, data: dict, jogo: Jogo) -> list[int]:
        """Extrai e normaliza as dezenas do JSON da Caixa."""
        if jogo == Jogo.FEDERAL:
            dezenas_raw = data.get("listaDezenas", [])
            dezenas = []
            for d in dezenas_raw:
                if isinstance(d, str):
                    dezenas.append(int(d))
                elif isinstance(d, int):
                    dezenas.append(d)
            return dezenas

        dezenas_raw = data.get("listaDezenas", [])
        dezenas = []
        for d in dezenas_raw:
            if isinstance(d, str):
                dezenas.append(int(d.lstrip("0") or "0"))
            elif isinstance(d, int):
                dezenas.append(d)
        return dezenas
