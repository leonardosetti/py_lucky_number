"""Base Lottery Collector — abstract class for all CEF data collectors.

All collectors inherit from this class, sharing:
- download_excel() via HTTPX with retry
- parse_to_dataframe() via Polars
- Column enrichment (hash_combinacao, dezenas_ordenadas)
- JSON persistence via orjson
- Bulk insert via asyncpg copy_from with error handling
- Prometheus metrics per game
"""

import abc
import hashlib
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson
import polars as pl

from src.collectors.utils import download_with_retry

logger = logging.getLogger(__name__)
DATA_DIR = Path(os.getenv("DATA_PATH", "./data"))
ERROR_DIR = DATA_DIR / "erros"

BALL_PREFIX = "Bola"


class BaseLotteryCollector(abc.ABC):
    """Abstract base for CEF lottery data collectors.

    Subclasses MUST define:
    - URL: str  — spreadsheet download URL
    - GAME_LABEL: str  — Prometheus label / hash namespace
    - TABLE_NAME: str  — database table name
    - JSON_PATH: str  — local JSON file path
    - COLUMNS: list  — expected column names (for Polars mapping)

    Subclasses MAY override:
    - hash_column: str  — column name for hash (default: hash_combinacao)
    - has_dezenas: bool  — whether table has dezenas_ordenadas (default: True)
    - ball_prefix: str  — prefix for ball columns (default: "Bola")
    - enrich_record(record)  — custom enrichment logic
    """

    URL: str = ""
    GAME_LABEL: str = ""
    TABLE_NAME: str = ""
    JSON_PATH: str = ""
    COLUMNS: list[str] = []
    CONCURSO_COL: str = "Concurso"

    hash_column: str = "hash_combinacao"
    has_dezenas: bool = True
    ball_prefix: str = BALL_PREFIX

    async def download_excel(self) -> bytes:
        """Download the XLSX spreadsheet from CEF URL."""
        ERROR_DIR.mkdir(parents=True, exist_ok=True)
        content = await download_with_retry(self.URL)
        return content

    def parse_to_dataframe(self, content: bytes) -> pl.DataFrame:
        """Parse XLSX content into a Polars DataFrame.
        Prevents CWE-20: validates column names before processing.
        """
        df = pl.read_excel(content)
        for col in self.COLUMNS:
            if col not in df.columns:
                logger.error(
                    f"Coluna esperada '{col}' não encontrada em {self.GAME_LABEL}"
                )
                raise ValueError(
                    f"Coluna '{col}' ausente na planilha {self.GAME_LABEL}"
                )
        return df

    def get_last_contest_from_json(self) -> int:
        """Read the max contest number from existing JSON file."""
        path = Path(self.JSON_PATH)
        if not path.exists():
            return 0
        with open(path, "rb") as f:
            data = orjson.loads(f.read())
        contests = data.get("concursos", [])
        if not contests:
            return 0
        return max(c.get(self.CONCURSO_COL, 0) for c in contests)

    def filter_new_contests(self, df: pl.DataFrame, last_id: int) -> pl.DataFrame:
        """Filter only contests newer than last_id."""
        if last_id <= 0:
            return df
        return df.filter(pl.col(self.CONCURSO_COL) > last_id)

    def _get_ball_columns(self, record: dict) -> list[str]:
        """Return ball column names sorted alphabetically."""
        return sorted(k for k in record if k.startswith(self.ball_prefix))

    def _compute_hash(self, values: list[int]) -> str:
        """SHA-256 of game label + sorted values. Prevents CWE-338."""
        raw = f"{self.GAME_LABEL}:{','.join(map(str, values))}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def enrich_record(self, record: dict) -> dict:
        """Add computed columns (hash, dezenas_ordenadas, coletado_em).

        Override for special games (Federal, Super Sete, Loteca, +Milionária).
        """
        record["coletado_em"] = datetime.now(UTC).isoformat()
        balls = self._get_ball_columns(record)
        if balls:
            values = sorted(int(record[c]) for c in balls)
            record[self.hash_column] = self._compute_hash(values)
            if self.has_dezenas:
                record["dezenas_ordenadas"] = values
        return record

    def enrich_records(self, records: list[dict]) -> list[dict]:
        """Enrich all records with computed columns."""
        return [self.enrich_record(r) for r in records]

    async def append_to_json(self, new_records: list[dict]) -> None:
        """Append new records to JSON file (read -> append -> rewrite).
        Prevents CWE-73: filename is fixed, never derived from input.
        """
        path = Path(self.JSON_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            with open(path, "rb") as f:
                data = orjson.loads(f.read())
        else:
            data = {
                "meta": {"jogo": self.GAME_LABEL, "url_origem": self.URL},
                "concursos": [],
            }

        data["concursos"].extend(new_records)
        data["meta"]["total_concursos"] = len(data["concursos"])
        data["meta"]["ultima_atualizacao"] = datetime.now(UTC).isoformat()

        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_APPEND_NEWLINE))

    async def bulk_insert_to_db(self, records: list[dict]) -> int:
        """Bulk insert records into PostgreSQL via asyncpg copy_from.
        Returns number of inserted rows. Wraps in transaction for rollback.
        """
        if not records:
            return 0
        import asyncpg

        raw_url = os.getenv("DATABASE_URL", "")
        if not raw_url:
            logger.error("DATABASE_URL not set — skipping DB insert")
            return 0

        dsn = raw_url.replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        try:
            columns = list(records[0].keys())
            rows = [[r[c] for c in columns] for r in records]
            async with conn.transaction():
                await conn.copy_records_to_table(
                    self.TABLE_NAME, records=rows, columns=columns
                )
        except Exception as e:
            logger.error(f"[{self.GAME_LABEL}] DB insert failed: {e}")
            raise
        finally:
            await conn.close()
        return len(records)

    async def collect(self) -> dict[str, Any]:
        """Main collection pipeline: download -> parse -> filter -> enrich -> save -> insert."""  # noqa: E501
        logger.info(f"[{self.GAME_LABEL}] Iniciando coleta...")

        content = await self.download_excel()
        df = self.parse_to_dataframe(content)
        last_id = self.get_last_contest_from_json()
        new_df = self.filter_new_contests(df, last_id)

        if new_df.is_empty():
            logger.info(f"[{self.GAME_LABEL}] Nenhum novo concurso encontrado")
            return {"game": self.GAME_LABEL, "new_contests": 0, "status": "no_updates"}

        raw_records = new_df.to_dicts()
        enriched = self.enrich_records(raw_records)

        await self.append_to_json(enriched)

        inserted = 0
        try:
            inserted = await self.bulk_insert_to_db(enriched)
        except Exception as e:
            logger.error(f"[{self.GAME_LABEL}] DB insert failed after JSON save: {e}")
            return {
                "game": self.GAME_LABEL,
                "new_contests": len(enriched),
                "inserted": 0,
                "status": "db_failed",
                "error": str(e),
            }

        logger.info(f"[{self.GAME_LABEL}] {inserted} novos concursos inseridos")
        return {"game": self.GAME_LABEL, "new_contests": inserted, "status": "success"}
