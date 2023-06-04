import time
from datetime import datetime, timedelta
from functools import wraps

from loguru import logger

from p0_backend.lib.errors.Protocol0Error import Protocol0Error


def log_exceptions(func):
    @wraps(func)
    def decorate(*a, **k):
        # noinspection PyBroadException
        try:
            func(*a, **k)
        except Exception as e:
            logger.exception(e)
            pass

    return decorate


class throttle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    """

    def __init__(self, milliseconds=0):
        self.throttle_period = timedelta(milliseconds=milliseconds)
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*a, **k):
            time_since_last_call = datetime.now() - self.time_of_last_call

            if time_since_last_call <= self.throttle_period:
                logger.info(f"{fn} throttled. time_since_last_call: {time_since_last_call}")
                return

            res = fn(*a, **k)
            self.time_of_last_call = datetime.now()
            return res

        return wrapper


def timeit(f):
    @wraps(f)
    def wrap(*a, **k):
        start_at = time.time()
        res = f(*a, **k)
        end_at = time.time()
        logger.info(f"func: {f.__name__} took: {end_at - start_at:.3f} sec")
        return res

    return wrap


def retry(count: int, duration: float):
    def decorator(func):
        @wraps(func)
        def wrap(*a, **k):
            assert count > 1, f"Expected count to be > 1, not {count}"

            exception = None

            for i in range(0, count):
                try:
                    return func(*a, **k)
                except (Protocol0Error, AssertionError) as e:
                    logger.warning(e)
                    time.sleep(duration)
                    logger.info(f"retry {i}/{count}")
                    exception = e

            raise exception

        return wrap

    return decorator
