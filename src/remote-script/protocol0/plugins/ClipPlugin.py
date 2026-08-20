"""Clip actions — operations on the selected clip.

Single-file drop-in plugin (no package, no ``__init__.py``), like ``DevicePlugin``.
It exposes ``POST /api/action/clip/remove_muted_notes``, so the action shows up in
the agent's action catalog and is bindable to a shortcut like any other action.

The logic is a one-liner over ``Song`` (as in ``TrackPlugin``), so there is no
domain service to delegate to: the note filtering itself lives on ``MidiClip``.
"""
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.shared.Song import Song


class ClipPlugin(PluginInterface):
    name = "clip"

    @action
    def remove_muted_notes(self) -> None:
        """Remove the muted notes of the selected MIDI clip."""
        Song.selected_clip(MidiClip).remove_muted_notes()
