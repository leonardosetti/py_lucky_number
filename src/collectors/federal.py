"""FederalCollector — 5 prêmios (sem bolas)."""
from src.collectors.base import BaseLotteryCollector


class FederalCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Federal"
    GAME_LABEL = "Federal"
    TABLE_NAME = "loterias_resultados_federal"
    JSON_PATH = "./data/federal.json"
    COLUMNS = ['Extração', 'Data Sorteio', '1º prêmio', 'Valor 1º prêmio', '2º prêmio', 'Valor 2º prêmio', '3º prêmio', 'Valor 3º prêmio', '4º prêmio', 'Valor 4º prêmio', '5º prêmio', 'Valor 5º prêmio']
    CONCURSO_COL = "Extração"
    hash_column = "hash_extracao"
    has_dezenas = False

    def enrich_record(self, record: dict) -> dict:
        record["coletado_em"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        extracao = record.get("Extração", 0)
        raw = f"Federal:{extracao}"
        import hashlib
        record["hash_extracao"] = hashlib.sha256(raw.encode()).hexdigest()
        return record
