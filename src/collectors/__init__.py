"""Data collectors for CEF lottery results."""

from src.collectors.base import BaseLotteryCollector
from src.collectors.megasena import MegasenaCollector
from src.collectors.lotofacil import LotofacilCollector
from src.collectors.quina import QuinaCollector
from src.collectors.duplasena import DuplasenaCollector
from src.collectors.diadesorte import DiadesorteCollector
from src.collectors.federal import FederalCollector
from src.collectors.lotomania import LotomaniaCollector
from src.collectors.timemania import TimemaniaCollector
from src.collectors.maismilionaria import MaismilionariaCollector
from src.collectors.supersete import SuperseteCollector
from src.collectors.loteca import LotecaCollector

__all__ = [
    "BaseLotteryCollector",
    "MegasenaCollector",
    "LotofacilCollector",
    "QuinaCollector",
    "DuplasenaCollector",
    "DiadesorteCollector",
    "FederalCollector",
    "LotomaniaCollector",
    "TimemaniaCollector",
    "MaismilionariaCollector",
    "SuperseteCollector",
    "LotecaCollector",
]
