from typing import Optional, Callable

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.control_surface.Encoders import Encoders
from protocol0.application.control_surface.MultiEncoder import MultiEncoder
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ActionGroupInterface(object):
    """
    An action group represents a group of 16 encoder available on my control_surface ec4
    It responds on a midi channel to cc messages
    See MultiEncoder to configure an encoder
    """

    CHANNEL: Optional[int] = None

    def __init__(self, container: ContainerInterface, component_guard: Callable) -> None:
        super(ActionGroupInterface, self).__init__()
        self._container = container
        self._component_guard = component_guard
        self._encoders = Encoders(component_guard)

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

    def add_encoder(
        self,
        identifier: int,
        name: str,
        on_press: Optional[Callable] = None,
        on_long_press: Optional[Callable] = None,
        on_scroll: Optional[Callable] = None,
        use_cc: bool = False,
        use_note_off: bool = False,
    ) -> MultiEncoder:
        """
        Declare an encoder of the group on the group's MIDI channel (CHANNEL is
        1-based, Encoders converts it to the 0-based MIDI channel).

        identifier: CC number of the encoder, unique within the group.
        name: human-readable name, used in logs and error messages.
        on_press / on_long_press / on_scroll: optional callbacks, each becoming
            an EncoderAction bound to the matching gesture.
        use_cc: the press arrives as a CC message instead of a note (no scroll).
        use_note_off: trigger the press action on release instead of press.
        """
        assert self.CHANNEL, "channel not configured for %s" % self
        return self._encoders.add_encoder(
            channel=self.CHANNEL,
            identifier=identifier,
            name=name,
            on_press=on_press,
            on_long_press=on_long_press,
            on_scroll=on_scroll,
            use_cc=use_cc,
            use_note_off=use_note_off,
        )

    def configure(self) -> None:
        raise NotImplementedError

    def _disconnect(self) -> None:
        self._encoders.disconnect()
