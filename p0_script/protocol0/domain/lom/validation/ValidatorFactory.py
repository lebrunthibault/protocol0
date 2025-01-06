from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.AbstractGroupTrackValidator import (
    AbstractGroupTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.SceneValidator import SceneValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import (
    SimpleAudioTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.SimpleTrackValidator import (
    SimpleTrackValidator,
)
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class ValidatorFactory(object):
    def __init__(self, browser_service: BrowserServiceInterface) -> None:
        self._browser_service = browser_service

    def create_from_object(self, obj: object) -> ValidatorInterface:
        if isinstance(obj, Scene):
            return SceneValidator(obj)

        # TRACKS
        elif isinstance(obj, SimpleAudioTrack):
            return SimpleAudioTrackValidator(obj)
        elif isinstance(obj, SimpleTrack):
            return SimpleTrackValidator(obj)
        elif isinstance(obj, AbstractGroupTrack):
            return AbstractGroupTrackValidator(obj)
        else:
            raise Protocol0Warning("%s is not handled by the object validator" % obj)
