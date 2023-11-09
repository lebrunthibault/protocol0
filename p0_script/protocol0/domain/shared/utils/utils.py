import itertools
import pkgutil
import re
import time
import types

from typing import Any, List, Callable, Iterable

from protocol0.domain.shared.utils.func import get_callable_repr
from protocol0.shared.Config import Config
from protocol0.shared.logging.Logger import Logger


def clamp(val: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(val, max_v))


def import_package(package: types.ModuleType) -> None:
    """import all modules in a package"""
    prefix = package.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        __import__(mod_name)


def locate(name: str) -> Any:
    components = name.split(".")
    mod = __import__(components[0])

    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod


def compare_values(value: Any, expected_value: Any) -> bool:
    if isinstance(value, float):
        value = round(value, 3)
        expected_value = round(expected_value, 3)

    return value == expected_value


def get_length_legend(beat_length: float, signature_numerator: int) -> str:
    if int(beat_length) % signature_numerator != 0:
        return "%d beat%s" % (beat_length, "s" if beat_length > 1 else "")
    else:
        return str(int(beat_length / signature_numerator))


def track_base_name(name: str, to_lower: bool = True) -> str:
    basename = re.sub(r"\s\d$", "", name.strip())
    if to_lower:
        return basename.lower()
    else:
        return basename


def get_minutes_legend(seconds: float) -> str:
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)

    return "%02d:%02d" % (minutes, seconds)


def volume_to_db(vol: float) -> float:
    if round(vol, 3) == round(Config.ZERO_VOLUME, 3):
        return 0

    return polynomial(
        vol,
        [
            3593.2,
            -18265.9,
            39231,
            -45962.3,
            31461.7,
            -12322.4,
            2371.63,
            -39.9082,
            Config.ZERO_VOLUME_DB,
        ],
    )


def db_to_volume(db: float) -> float:
    if db == 0:
        return Config.ZERO_VOLUME

    if db < -60:
        return 0

    return polynomial(
        db,
        [
            -1.419398502456 * pow(10, -10),
            -1.8321104871497 * pow(10, -8),
            -7.93316011830 * pow(10, -7),
            -0.0000133509,
            -0.0000590049,
            0.000480888,
            0.0282999,
            0.85,
        ],
    )


def polynomial(x: float, coeffs: List[float]) -> float:
    """Using polynomial interpolation"""
    coeffs = list(reversed(coeffs))

    def make_term(val: float, index: int) -> float:
        term = coeffs[index]
        if index > 0:
            term *= pow(val, index)
        return term

    return sum([make_term(x, i) for i in range(len(coeffs))])


def previous_power_of_2(x: int) -> int:
    if x == 0:
        return 0

    res = 2 ** (x - 1).bit_length()

    if x == res or x == res * 3 / 4:
        return x
    else:
        return int(res / 2)


def timeit(func: Callable) -> Callable:
    def decorate(*a: Any, **k: Any) -> None:
        start_at = time.time()
        res = func(*a, **k)

        duration = time.time() - start_at
        Logger.info("%s took %.3fs" % (get_callable_repr(func), duration))

        return res

    return decorate


def float_seq(start: int, end: int, step: float) -> Iterable:
    assert step != 0
    sample_count = int(abs(end - start) / step)

    return itertools.islice(itertools.count(start, step), sample_count)
