from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.shared.Song import Song


class ActionGroupClip(ActionGroupInterface):
    CHANNEL = 7

    def configure(self) -> None:
        # DUPLicate clip
        self.add_encoder(
            identifier=1,
            name="duplicate clip",
            on_press=lambda: Song.selected_track().broadcast_selected_clip,
        )

        # midi clip to MONO
        self.add_encoder(
            identifier=4,
            name="midi clip to mono",
            on_press=lambda: Song.selected_clip(MidiClip).to_mono,
        )

        # midi clip to MONO
        # todo: remove
        self.add_encoder(
            identifier=13,
            name="link clips automation",
            on_press=lambda: Song.selected_track().link_automation,
        )
