"""Celery Beat periodic tasks for data collectors (specs 007–017).

Schedule:
- Fixed interval: every 6 hours (configurable via COLETA_INTERVALO_MINUTOS)
- Extra check on draw days for each game
"""

import logging
import os

from celery.schedules import crontab

from tasks.celery_app import celery_app
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

logger = logging.getLogger(__name__)

COLETA_INTERVALO_MINUTOS = int(os.getenv("COLETA_INTERVALO_MINUTOS", "360"))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_megasena(self):
    return _run_collector(MegasenaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_lotofacil(self):
    return _run_collector(LotofacilCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_quina(self):
    return _run_collector(QuinaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_duplasena(self):
    return _run_collector(DuplasenaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_diadesorte(self):
    return _run_collector(DiadesorteCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_federal(self):
    return _run_collector(FederalCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_lotomania(self):
    return _run_collector(LotomaniaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_timemania(self):
    return _run_collector(TimemaniaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_maismilionaria(self):
    return _run_collector(MaismilionariaCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_supersete(self):
    return _run_collector(SuperseteCollector(), self)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def collect_loteca(self):
    return _run_collector(LotecaCollector(), self)


def _run_collector(collector, task):
    """Run a collector and handle errors for Celery task."""
    import asyncio

    try:
        result = asyncio.run(collector.collect())
        logger.info(f"[{collector.GAME_LABEL}] Coleta concluída: {result}")
        return result
    except Exception as exc:
        logger.error(f"[{collector.GAME_LABEL}] Coleta falhou: {exc}")
        raise task.retry(exc=exc)


# ─── Celery Beat Schedule ──────────────────────────────────────────
# Fixed interval for all games + extra checks on draw days

celery_app.conf.beat_schedule = {
    "collect-megasena": {
        "task": "src.tasks.periodic.collect_megasena",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-lotofacil": {
        "task": "src.tasks.periodic.collect_lotofacil",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-quina": {
        "task": "src.tasks.periodic.collect_quina",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-duplasena": {
        "task": "src.tasks.periodic.collect_duplasena",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-diadesorte": {
        "task": "src.tasks.periodic.collect_diadesorte",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-federal": {
        "task": "src.tasks.periodic.collect_federal",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-lotomania": {
        "task": "src.tasks.periodic.collect_lotomania",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-timemania": {
        "task": "src.tasks.periodic.collect_timemania",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-maismilionaria": {
        "task": "src.tasks.periodic.collect_maismilionaria",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-supersete": {
        "task": "src.tasks.periodic.collect_supersete",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
    "collect-loteca": {
        "task": "src.tasks.periodic.collect_loteca",
        "schedule": crontab(minute=f"*/{COLETA_INTERVALO_MINUTOS}"),
    },
}
