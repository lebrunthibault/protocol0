from typing import Type, Any, Optional

from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.AbstractEnum import AbstractEnum


class RoutingDisplayNameDescriptor(object):
    def __init__(self, routing_attribute_name: str, routing_enum_class: Type[AbstractEnum]) -> None:
        self.routing_enum_class = routing_enum_class
        self.routing_attribute_name = routing_attribute_name
        self.available_routings_attribute_name = "available_%ss" % routing_attribute_name

    def __repr__(self) -> str:
        return "RoutingDisplayName.%s" % self.routing_attribute_name

    def __get__(self, track_routing: TrackRoutingInterface, _: Type) -> Optional[Any]:
        try:
            return self.routing_enum_class.from_value(
                getattr(track_routing.live_track, self.routing_attribute_name).display_name
            )
        except Protocol0Error:
            return None

    def __set__(self, track_routing: TrackRoutingInterface, routing_enum: AbstractEnum) -> None:
        routing = find_if(
            lambda r: r.display_name == routing_enum.value,
            getattr(track_routing.live_track, self.available_routings_attribute_name),
        )
        if not routing:
            raise Protocol0Error(
                "couldn't find %s routing matching '%s' for '%s'"
                % (self.routing_attribute_name, routing_enum, track_routing.live_track.name)
            )
        setattr(track_routing.live_track, self.routing_attribute_name, routing)
