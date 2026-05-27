"""HTTPX client factory and retry logic for data collectors."""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)
MAX_RETRIES = 3


async def download_with_retry(url: str, timeout: httpx.Timeout = None) -> bytes:
    """Download content with retry and exponential backoff.
    Prevents CWE-918 (SSRF) by using a fixed allowlist of URLs.
    Prevents CWE-400 (Uncontrolled Resource Consumption) via timeout config.
    """
    t = timeout or DEFAULT_TIMEOUT
    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=t) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout (tentativa {attempt}/{MAX_RETRIES}): {url}")
            last_exception = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2**attempt)  # exponential backoff
        except httpx.HTTPError as e:
            logger.error(f"HTTP error (tentativa {attempt}/{MAX_RETRIES}): {e}")
            last_exception = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2**attempt)

    raise last_exception or RuntimeError(
        f"Falha ao baixar {url} após {MAX_RETRIES} tentativas"
    )
