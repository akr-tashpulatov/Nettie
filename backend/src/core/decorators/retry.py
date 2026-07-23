import functools

from src.core.logger import logging


def retry(times: int, exceptions: tuple[type[Exception], ...]):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """

    def decorator(func):
        @functools.wraps(func)
        async def newfn(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    logging.warning(
                        "Exception in %s, attempt %d of %d: %s",
                        func.__qualname__,
                        attempt,
                        times,
                        exc,
                    )
                    if attempt == times:
                        raise

        return newfn

    return decorator
