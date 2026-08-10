from typing import Callable, List, Optional, Tuple

from protocol0.application.control_surface.EncoderAction import EncoderAction
from protocol0.application.control_surface.MultiEncoder import MultiEncoder


class Encoders(object):
    """Owns MultiEncoders bound to the control surface.

    This is the encoder-binding machinery shared by action groups (see
    ActionGroupInterface) and plugins (see PluginInterface.register_encoders):
    it wires physical encoders to gesture callbacks and disconnects them all
    at once on teardown.
    """

    def __init__(self, component_guard: Callable) -> None:
        self._component_guard = component_guard
        self._multi_encoders: List[MultiEncoder] = []
        self._keys: List[Tuple[int, int]] = []

    def __len__(self) -> int:
        return len(self._multi_encoders)

    def add_encoder(
        self,
        channel: int,
        identifier: int,
        name: str,
        on_press: Optional[Callable] = None,
        on_long_press: Optional[Callable] = None,
        on_scroll: Optional[Callable] = None,
        use_cc: bool = False,
        use_note_off: bool = False,
        scroll_only: bool = False,
    ) -> MultiEncoder:
        """
        Declare an encoder on a MIDI channel (1-based, converted here to the
        0-based MIDI channel).

        identifier: CC number of the encoder, unique per channel.
        name: human-readable name, used in logs and error messages.
        on_press / on_long_press / on_scroll: optional callbacks, each becoming
            an EncoderAction bound to the matching gesture.
        use_cc: the press arrives as a CC message instead of a note (no scroll).
        use_note_off: trigger the press action on release instead of press.
        scroll_only: listen only to the rotation CC — no press element. Required
            for CC 0, whose press note would be identifier - 1 = -1.
        """
        assert channel, "channel not configured for encoder %s" % name
        key = (channel, identifier)
        assert key not in self._keys, "duplicate encoder ch.%s cc.%s (%s)" % (
            channel,
            identifier,
            name,
        )
        encoder = MultiEncoder(
            channel=channel - 1,
            identifier=identifier,
            name=name,
            component_guard=self._component_guard,
            use_cc=use_cc,
            use_note_off=use_note_off,
            scroll_only=scroll_only,
        )
        for action in EncoderAction.make_actions(
            name=name, on_press=on_press, on_long_press=on_long_press, on_scroll=on_scroll
        ):
            encoder.add_action(action)
        self._multi_encoders.append(encoder)
        self._keys.append(key)
        return encoder

    def disconnect(self) -> None:
        for encoder in self._multi_encoders:
            encoder.disconnect()
        self._multi_encoders = []
        self._keys = []
