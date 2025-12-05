# app/resilience.py
import time
import asyncio
import logging
from typing import Callable, Type, Tuple, Any

logger = logging.getLogger("retry")


class RetryConfig:
    """
    Configuração para o mecanismo de retry com backoff exponencial.
    """

    def __init__(
        self,
        retries: int = 3,
        delay_seconds: float = 0.5,
        backoff_factor: float = 2.0,
        retry_on_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    ):
        if retries < 1:
            raise ValueError("Retries must be at least 1.")
        if delay_seconds <= 0:
            raise ValueError("Delay must be > 0.")
        if backoff_factor <= 1:
            raise ValueError("Backoff factor must be > 1.")

        self.retries = retries
        self.delay_seconds = delay_seconds
        self.backoff_factor = backoff_factor
        self.retry_on_exceptions = retry_on_exceptions


def retry(config: RetryConfig):
    """
    Decorator para aplicar retry com backoff exponencial.
    Funciona com funções síncronas e assíncronas.
    """

    def decorator(func: Callable):
        is_async = asyncio.iscoroutinefunction(func)

        async def async_wrapper(*args, **kwargs):
            delay = config.delay_seconds

            for attempt in range(1, config.retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    logger.warning(
                        f"Tentativa {attempt} falhou: {e}. Nova tentativa em {delay:.2f}s."
                    )
                    if attempt == config.retries:
                        raise
                    await asyncio.sleep(delay)
                    delay *= config.backoff_factor

        def sync_wrapper(*args, **kwargs):
            delay = config.delay_seconds

            for attempt in range(1, config.retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retry_on_exceptions as e:
                    logger.warning(
                        f"Tentativa {attempt} falhou: {e}. Nova tentativa em {delay:.2f}s."
                    )
                    if attempt == config.retries:
                        raise
                    time.sleep(delay)
                    delay *= config.backoff_factor

        return async_wrapper if is_async else sync_wrapper

    return decorator
