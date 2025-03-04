import json
import time
from typing import List, Optional, Callable

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.EncoderAction import EncoderAction, EncoderMoveEnum
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class MultiEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(
        self,
        channel: int,
        identifier: int,
        name: str,
        component_guard: Callable,
        use_cc: bool,
        use_note_off: bool,
    ) -> None:
        """
        Actions are triggered at the start of the press except when a long_press is declared.
        """
        super(MultiEncoder, self).__init__()
        self._actions: List[EncoderAction] = []
        self.identifier = identifier
        self.name = name.title()
        self._channel = channel
        self._use_note_off = use_note_off

        with component_guard():
            if use_cc:
                self._press_listener.subject = ButtonElement(
                    True, MIDI_CC_TYPE, channel, identifier
                )
            else:
                self._press_listener.subject = ButtonElement(
                    True, MIDI_NOTE_TYPE, channel, identifier
                )
                self._scroll_listener.subject = ButtonElement(
                    True, MIDI_CC_TYPE, channel, identifier
                )

        self._pressed_at: Optional[float] = None
        self._has_long_press = False

    def __repr__(self) -> str:
        return json.dumps({"channel": self._channel, "name": self.name, "id": self.identifier})

    def add_action(self, action: EncoderAction) -> "MultiEncoder":
        assert self._find_matching_action(action.move_type) is None, "duplicate move %s" % action
        if action.move_type == EncoderMoveEnum.LONG_PRESS:
            self._has_long_press = True
        self._actions.append(action)
        return self

    @property
    def _is_long_pressed(self) -> bool:
        return bool(
            self._pressed_at
            and (time.time() - self._pressed_at) > MultiEncoder.LONG_PRESS_THRESHOLD
        )

    @subject_slot("value")
    def _press_listener(self, value: int) -> None:
        """On long press, or using use_note_off, act on release, else act on press"""
        if value:  # press (Note on)
            if self._has_long_press:
                self._pressed_at = time.time()
            elif not self._use_note_off:
                self._find_and_execute_action(move_type=EncoderMoveEnum.PRESS)
        else:  # release (Note off)
            if self._has_long_press:
                # action executed on press and not release when only press defined
                move_type = (
                    EncoderMoveEnum.LONG_PRESS if self._is_long_pressed else EncoderMoveEnum.PRESS
                )
                self._find_and_execute_action(move_type=move_type)
            elif self._use_note_off:
                self._find_and_execute_action(move_type=EncoderMoveEnum.PRESS)

    @subject_slot("value")
    def _scroll_listener(self, value: int) -> None:
        self._find_and_execute_action(move_type=EncoderMoveEnum.SCROLL, go_next=value == 1)

    def _find_and_execute_action(
        self, move_type: EncoderMoveEnum, go_next: Optional[bool] = None
    ) -> None:
        # noinspection PyBroadException
        try:
            action = self._find_matching_action(move_type=move_type)
            # special case : fallback long_press to press
            if not action and move_type == EncoderMoveEnum.LONG_PRESS:
                action = self._find_matching_action(move_type=EncoderMoveEnum.PRESS)

            if not action:
                raise Protocol0Warning("Action not found: %s (%s)" % (self.name, move_type))

            self._pressed_at = None
            if not action:
                return None

            params = {}
            if go_next is not None:
                params["go_next"] = go_next

            action.execute(encoder_name=self.name, **params)
        except Exception as e:  # noqa
            DomainEventBus.emit(ErrorRaisedEvent())

    def _find_matching_action(self, move_type: EncoderMoveEnum) -> Optional[EncoderAction]:
        actions = [
            encoder_action
            for encoder_action in self._actions
            if encoder_action.move_type == move_type
        ]
        return next(iter(actions), None)
