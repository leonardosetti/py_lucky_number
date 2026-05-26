"""MaismilionariaCollector — 6 números + 2 trevos."""
import hashlib

from src.collectors.base import BaseLotteryCollector


class MaismilionariaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Mais-Milionaria"
    GAME_LABEL = "Maismilionaria"
    TABLE_NAME = "loterias_resultados_maismilionaria"
    JSON_PATH = "./data/maismilionaria.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Trevo1', 'Trevo2']
    CONCURSO_COL = "Concurso"

    def enrich_record(self, record: dict) -> dict:
        from datetime import UTC, datetime
        record["coletado_em"] = datetime.now(UTC).isoformat()

        balls = sorted(int(record[f"Bola{i}"]) for i in range(1, 7))
        trevos = sorted(int(record[f"Trevo{i}"]) for i in range(1, 3))

        raw = f"{self.GAME_LABEL}:{','.join(map(str, balls))}+{','.join(map(str, trevos))}"
        record[self.hash_column] = hashlib.sha256(raw.encode()).hexdigest()
        record["dezenas_ordenadas"] = balls
        record["trevos_ordenados"] = trevos
        return record
