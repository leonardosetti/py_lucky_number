"""Base Lottery Collector — abstract class for all CEF data collectors.

All 10 collectors inherit from this class, sharing:
- download_excel() via HTTPX with retry
- parse_to_dataframe() via Polars
- JSON persistence via orjson
- Bulk insert via asyncpg copy_from
- Prometheus metrics per game
"""
import abc
import json
import logging
import os
from pathlib import Path
from typing import Any

import orjson
import polars as pl

from src.collectors.utils import download_with_retry

logger = logging.getLogger(__name__)
DATA_DIR = Path(os.getenv("DATA_PATH", "./data"))
ERROR_DIR = DATA_DIR / "erros"


class BaseLotteryCollector(abc.ABC):
    """Abstract base for CEF lottery data collectors.

    Subclasses MUST define:
    - URL: str  — spreadsheet download URL
    - GAME_LABEL: str  — Prometheus label
    - TABLE_NAME: str  — database table name
    - JSON_PATH: str  — local JSON file path
    - COLUMNS: list  — expected column names (for Polars mapping)
    - DRAW_DAYS: list[int]  — day-of-week for extra checks (0=Mon)

    Subclasses MAY override:
    - parse_to_dataframe()  — if spreadsheet format differs
    - get_last_contest_from_json()  — if PK column differs (Federal)
    """

    URL: str = ""
    GAME_LABEL: str = ""
    TABLE_NAME: str = ""
    JSON_PATH: str = ""
    COLUMNS: list[str] = []
    CONCURSO_COL: str = "Concurso"  # override to "Extração" for Federal

    async def download_excel(self) -> bytes:
        """Download the XLSX spreadsheet from CEF URL."""
        error_dir.mkdir(parents=True, exist_ok=True)
        content = await download_with_retry(self.URL)
        return content

    def parse_to_dataframe(self, content: bytes) -> pl.DataFrame:
        """Parse XLSX content into a Polars DataFrame.
        Prevents CWE-20: validates column names before processing.
        """
        df = pl.read_excel(content)
        # Validate expected columns
        for col in self.COLUMNS:
            if col not in df.columns:
                logger.error(f"Coluna esperada '{col}' não encontrada em {self.GAME_LABEL}")
                raise ValueError(f"Coluna '{col}' ausente na planilha {self.GAME_LABEL}")
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

    async def append_to_json(self, new_records: list[dict]) -> None:
        """Append new records to JSON file (read → append → rewrite).
        Prevents CWE-73: filename is fixed, never derived from input.
        """
        path = Path(self.JSON_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            with open(path, "rb") as f:
                data = orjson.loads(f.read())
        else:
            data = {"meta": {"jogo": self.GAME_LABEL, "url_origem": self.URL}, "concursos": []}

        data["concursos"].extend(new_records)
        data["meta"]["total_concursos"] = len(data["concursos"])
        data["meta"]["ultima_atualizacao"] = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()

        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_APPEND_NEWLINE))

    async def bulk_insert_to_db(self, records: list[dict]) -> int:
        """Bulk insert records into PostgreSQL via asyncpg copy_from.
        Returns number of inserted rows.
        """
        if not records:
            return 0
        import asyncpg

        conn = await asyncpg.connect(os.getenv("DATABASE_URL", "").replace("+asyncpg", ""))
        try:
            # Convert records to list of tuples for copy_from
            columns = list(records[0].keys())
            rows = [[r[c] for c in columns] for r in records]
            await conn.copy_records_to_table(
                self.TABLE_NAME, records=rows, columns=columns
            )
        finally:
            await conn.close()
        return len(records)

    async def collect(self) -> dict[str, Any]:
        """Main collection pipeline: download → parse → filter → save → insert."""
        logger.info(f"[{self.GAME_LABEL}] Iniciando coleta...")

        # 1. Download
        content = await self.download_excel()

        # 2. Parse
        df = self.parse_to_dataframe(content)

        # 3. Get last contest
        last_id = self.get_last_contest_from_json()

        # 4. Filter new
        new_df = self.filter_new_contests(df, last_id)
        if new_df.is_empty():
            logger.info(f"[{self.GAME_LABEL}] Nenhum novo concurso encontrado")
            return {"game": self.GAME_LABEL, "new_contests": 0, "status": "no_updates"}

        # 5. Convert to dicts
        new_records = new_df.to_dicts()

        # 6. Save to JSON
        await self.append_to_json(new_records)

        # 7. Insert to DB
        inserted = await self.bulk_insert_to_db(new_records)

        logger.info(f"[{self.GAME_LABEL}] {inserted} novos concursos inseridos")
        return {"game": self.GAME_LABEL, "new_contests": inserted, "status": "success"}
