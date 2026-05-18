"""TimemaniaCollector — 7 bolas + Time Coração."""
from src.collectors.base import BaseLotteryCollector


class TimemaniaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Timemania"
    GAME_LABEL = "Timemania"
    TABLE_NAME = "loterias_resultados_timemania"
    JSON_PATH = "./data/timemania.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Bola7', 'Time Coração']
    CONCURSO_COL = "Concurso"
