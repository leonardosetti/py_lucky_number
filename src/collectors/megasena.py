"""MegasenaCollector — 6 bolas."""

from src.collectors.base import BaseLotteryCollector


class MegasenaCollector(BaseLotteryCollector):
    URL = "https://servicebus3.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Dia-De-Sorte"  # noqa: E501  # noqa: E501
    GAME_LABEL = "Megasena"
    TABLE_NAME = "loterias_resultados_megasena"
    JSON_PATH = "./data/megasena.json"
    COLUMNS = [
        "Concurso",
        "Data do Sorteio",
        "Bola1",
        "Bola2",
        "Bola3",
        "Bola4",
        "Bola5",
        "Bola6",
    ]
    CONCURSO_COL = "Concurso"
