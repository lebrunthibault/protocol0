from typing import List, Optional, Callable

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.control_surface.EncoderAction import EncoderAction
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
        self._multi_encoders: List[MultiEncoder] = []

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

    def _add_multi_encoder(self, multi_encoder: MultiEncoder) -> MultiEncoder:
        assert (
            len(
                [
                    encoder
                    for encoder in self._multi_encoders
                    if encoder.identifier == multi_encoder.identifier
                ]
            )
            == 0
        ), f"duplicate multi encoder id : {multi_encoder}"
        self._multi_encoders.append(multi_encoder)
        return multi_encoder

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
        assert self.CHANNEL, "channel not configured for %s" % self
        encoder = MultiEncoder(
            channel=self.CHANNEL - 1,
            identifier=identifier,
            name=name,
            component_guard=self._component_guard,
            use_cc=use_cc,
            use_note_off=use_note_off,
        )
        for action in EncoderAction.make_actions(
            name=name, on_press=on_press, on_long_press=on_long_press, on_scroll=on_scroll
        ):
            encoder.add_action(action)
        return self._add_multi_encoder(encoder)

    def configure(self) -> None:
        raise NotImplementedError

    def _disconnect(self) -> None:
        for encoder in self._multi_encoders:
            encoder.disconnect()
