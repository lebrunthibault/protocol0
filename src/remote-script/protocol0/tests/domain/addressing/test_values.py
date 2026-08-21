import pytest

from protocol0.domain.lom.addressing.values import (
    resolve_adjustable,
    resolve_bool,
    resolve_continuous,
    resolve_quasi_continuous,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


@pytest.mark.parametrize(
    "spec, current, expected",
    [
        ("ON", False, True),
        ("on", False, True),
        ("OFF", True, False),
        ("TGL", True, False),
        ("TGL", False, True),
        ("", True, False),  # empty defaults to toggle
        ("true", False, True),
        ("0", True, False),
    ],
)
def test_resolve_bool(spec, current, expected):
    assert resolve_bool(spec, current) is expected


def test_resolve_bool_invalid():
    with pytest.raises(Protocol0Warning):
        resolve_bool("MAYBE", False)


@pytest.mark.parametrize(
    "spec, current, expected",
    [
        ("0.5", 0.0, 0.5),  # absolute
        ("2", 0.0, 1.0),  # absolute clamped to max
        ("-1", 0.5, 0.0),  # absolute clamped to min
        ("50%", 0.0, 0.5),  # percent of range
        ("100%", 0.0, 1.0),
        (">", 0.5, 0.5 + 1 / 64),  # one step = range/64
        ("<", 0.5, 0.5 - 1 / 64),
        (">8", 0.5, 0.5 + 8 / 64),
        ("<16", 0.5, 0.25),
        (">64", 0.9, 1.0),  # step clamped
        ("RESET", 0.9, 0.25),
    ],
)
def test_resolve_continuous(spec, current, expected):
    result = resolve_continuous(spec, current, 0.0, 1.0, default=0.25)
    assert result == pytest.approx(expected)


def test_resolve_continuous_random_stays_in_range():
    for _ in range(20):
        assert 0.0 <= resolve_continuous("RND", 0.5, 0.0, 1.0) <= 1.0
        assert 0.25 <= resolve_continuous("RND25-75", 0.5, 0.0, 1.0) <= 0.75


def test_resolve_continuous_invalid():
    with pytest.raises(Protocol0Warning):
        resolve_continuous("loud", 0.5, 0.0, 1.0)


@pytest.mark.parametrize(
    "spec, current, expected",
    [
        ("120", 100.0, 120.0),  # absolute display units (BPM)
        (">", 120.0, 121.0),  # one unit
        ("<", 120.0, 119.0),
        (">10", 120.0, 130.0),
        ("<5", 120.0, 115.0),
        ("500", 100.0, 200.0),  # clamped to max
    ],
)
def test_resolve_quasi_continuous(spec, current, expected):
    assert resolve_quasi_continuous(spec, current, 20.0, 200.0) == pytest.approx(expected)


_MONITORING = ["in", "auto", "off"]


@pytest.mark.parametrize(
    "spec, current, expected",
    [
        ("auto", "in", "auto"),
        ("AUTO", "in", "auto"),  # case-insensitive
        (">", "in", "auto"),  # cycles forward
        (">", "off", "in"),  # wraps around
        ("<", "in", "off"),  # wraps backward
    ],
)
def test_resolve_adjustable(spec, current, expected):
    assert resolve_adjustable(spec, _MONITORING, current) == expected


def test_resolve_adjustable_invalid():
    with pytest.raises(Protocol0Warning):
        resolve_adjustable("loud", _MONITORING, "in")
