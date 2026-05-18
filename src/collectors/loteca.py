"""LotecaCollector — 7 colunas, semanal, janela crítica Dom 20h–Seg 23h."""
from src.collectors.base import BaseLotteryCollector


class LotecaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Loteca"
    GAME_LABEL = "Loteca"
    TABLE_NAME = "loterias_resultados_loteca"
    JSON_PATH = "./data/loteca.json"
    COLUMNS = ["Concurso", "Data Sorteio", "Coluna 1", "Coluna 2", "Coluna 3", "Coluna 4", "Coluna 5", "Coluna 6", "Coluna 7"]
    CONCURSO_COL = "Concurso"
    # Critical window: Sunday 20h → Monday 23h, check every 90min
    CRITICAL_WINDOW_START = (6, 20)  # Sunday 20:00
    CRITICAL_WINDOW_END = (0, 23)    # Monday 23:00
