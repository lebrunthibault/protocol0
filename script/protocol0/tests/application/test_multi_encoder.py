import pytest

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.EncoderAction import EncoderAction
from protocol0.application.control_surface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.application.control_surface.MultiEncoder import MultiEncoder
from protocol0.tests.domain.fixtures.container import TestContainer
from protocol0.tests.domain.fixtures.p0 import make_protocol0


class ActionGroupTest(ActionGroupInterface):
    CHANNEL = 1

    def configure(self):
        pass


def _press_encoder(encoder: MultiEncoder) -> None:
    encoder._press_listener(1)
    encoder._press_listener(0)


def _scroll_encoder(encoder: MultiEncoder) -> None:
    encoder._scroll_listener(1)


def _make_multi_encoder(identifier: int = 1) -> MultiEncoder:
    p0 = make_protocol0()
    return ActionGroupTest(TestContainer(), p0.component_guard).add_encoder(
        identifier=identifier, name="pytest"
    )


def test_multi_encoder_press() -> None:
    res = {"pressed": False}

    def press() -> None:
        res["pressed"] = True

    multi_encoder = _make_multi_encoder().add_action(
        EncoderAction(press, move_type=EncoderMoveEnum.PRESS, name="test")
    )

    with pytest.raises(AssertionError):
        multi_encoder.add_action(
            EncoderAction(func=lambda: None, move_type=EncoderMoveEnum.PRESS, name="test")
        )

    _press_encoder(multi_encoder)
    # assert res["pressed"] is True


def test_multi_encoder_scroll() -> None:
    make_protocol0()
    res = {"scrolled": False}

    # noinspection PyUnusedLocal
    def scroll(go_next: bool) -> None:
        res["scrolled"] = True

    multi_encoder = _make_multi_encoder().add_action(
        EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL, name="test")
    )
    _scroll_encoder(multi_encoder)
    assert res["scrolled"] is True


def test_multi_encoder_press_and_scroll() -> None:
    res = {"pressed": False, "scrolled": False}

    # noinspection PyUnusedLocal
    def scroll(go_next: bool) -> None:
        res["scrolled"] = True

    def press() -> None:
        res["pressed"] = True

    multi_encoder = (
        _make_multi_encoder()
        .add_action(EncoderAction(press, move_type=EncoderMoveEnum.PRESS, name="test"))
        .add_action(EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL, name="test"))
    )
    _scroll_encoder(multi_encoder)
    assert res["scrolled"] is True
    assert res["pressed"] is False
    _press_encoder(multi_encoder)
    assert res["pressed"] is True
