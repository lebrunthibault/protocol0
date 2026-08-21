"""Uniform value grammar of the action catalog (ClyphX-modeled tiers).

One vocabulary for every action instead of per-action conventions:

- bool tier        ON | OFF | TGL (toggles, default)
- continuous tier  absolute x | x% | < / > (one step = range/64) | <x / >x |
                   RND | RNDx-y (percent range) | RESET (back to default)
- quasi-continuous display units (BPM, dB): absolute | < / > | <x / >x
- adjustable tier  enumerated options: exact name | < / > cycling
"""
import random

from typing import List, Tuple

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning

# a < / > nudge moves by range/64, like ClyphX's default step on 0-127 params
_CONTINUOUS_STEPS = 64


def resolve_bool(spec: str, current: bool) -> bool:
    spec = (spec or "TGL").strip().upper()
    if spec in ("ON", "TRUE", "1"):
        return True
    if spec in ("OFF", "FALSE", "0"):
        return False
    if spec in ("TGL", "TOGGLE", ""):
        return not current
    raise Protocol0Warning("invalid bool value '%s' (expected ON, OFF or TGL)" % spec)


def resolve_continuous(
    spec: str, current: float, min_value: float, max_value: float, default: float = None
) -> float:
    spec = (spec or "").strip()
    keyword = spec.upper()
    value_range = max_value - min_value

    if keyword == "RESET":
        if default is None:
            raise Protocol0Warning("this parameter has no default value to RESET to")
        return default
    if keyword == "RND":
        return random.uniform(min_value, max_value)
    if keyword.startswith("RND") and "-" in keyword:
        low, high = _parse_percent_range(keyword[len("RND") :])
        return min_value + value_range * random.uniform(low, high) / 100.0
    if keyword.startswith("<") or keyword.startswith(">"):
        steps = _parse_steps(keyword)
        return _clamp(current + steps * value_range / _CONTINUOUS_STEPS, min_value, max_value)
    if spec.endswith("%"):
        return _clamp(min_value + value_range * _parse_number(spec[:-1]) / 100.0, min_value, max_value)
    return _clamp(_parse_number(spec), min_value, max_value)


def resolve_quasi_continuous(
    spec: str, current: float, min_value: float, max_value: float
) -> float:
    """Display-unit tier (BPM, dB): absolute values and unit steps, no %/random."""
    spec = (spec or "").strip()
    if spec.startswith("<") or spec.startswith(">"):
        return _clamp(current + _parse_steps(spec), min_value, max_value)
    return _clamp(_parse_number(spec), min_value, max_value)


def resolve_adjustable(spec: str, options: List[str], current: str) -> str:
    """Enumerated tier: exact option name (case-insensitive) or < / > cycling."""
    spec = (spec or "").strip()
    if spec in ("<", ">"):
        if current not in options:
            return options[0]
        offset = 1 if spec == ">" else -1
        return options[(options.index(current) + offset) % len(options)]
    matches = [option for option in options if option.lower() == spec.lower()]
    if not matches:
        raise Protocol0Warning(
            "invalid value '%s' (options: %s)" % (spec, ", ".join(options))
        )
    return matches[0]


def _parse_steps(spec: str) -> float:
    """'<' -> -1, '>' -> +1, '<x' / '>x' -> -x / +x."""
    sign = -1 if spec[0] == "<" else 1
    body = spec[1:].strip()
    return sign * (_parse_number(body) if body else 1)


def _parse_number(text: str) -> float:
    try:
        return float(text.strip())
    except ValueError:
        raise Protocol0Warning("invalid numeric value '%s'" % text.strip())


def _parse_percent_range(text: str) -> Tuple[float, float]:
    low, _, high = text.partition("-")
    return _parse_number(low), _parse_number(high)


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))
