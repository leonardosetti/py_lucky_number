"""LotofacilCollector — 15 bolas."""
from src.collectors.base import BaseLotteryCollector


class LotofacilCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil"
    GAME_LABEL = "Lotofacil"
    TABLE_NAME = "loterias_resultados_lotofacil"
    JSON_PATH = "./data/lotofacil.json"
    COLUMNS = ['Concurso', 'Data Sorteio', 'Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Bola7', 'Bola8', 'Bola9', 'Bola10', 'Bola11', 'Bola12', 'Bola13', 'Bola14', 'Bola15']
    CONCURSO_COL = "Concurso"
