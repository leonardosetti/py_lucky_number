"""QuinaCollector — 5 bolas."""
from src.collectors.base import BaseLotteryCollector


class QuinaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Quina"
    GAME_LABEL = "Quina"
    TABLE_NAME = "loterias_resultados_quina"
    JSON_PATH = "./data/quina.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5']
    CONCURSO_COL = "Concurso"
