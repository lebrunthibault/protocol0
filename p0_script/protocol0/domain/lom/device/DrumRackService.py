from functools import partial
from typing import cast, Optional

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class DrumRackService(object):
    def __init__(self, browser_service: BrowserServiceInterface) -> None:
        self._browser_service = browser_service

    def drum_rack_to_simpler(self, track: SimpleTrack) -> Optional[Sequence]:
        assert track.instrument
        device = cast(DrumRackDevice, track.instrument.device)
        if not isinstance(device, DrumRackDevice):
            raise Protocol0Warning("Selected device should be a drum rack")
        assert track == Song.selected_track(), "track should already be selected"

        pitches = list(
            set(note.pitch for clip in track.clips for note in cast(MidiClip, clip).get_notes())
        )

        if len(pitches) != 1:
            Backend.client().show_warning(
                "Expected only one pitch used, got %s in %s clips"
                % (len(pitches), len(track.clips))
            )
            return None

        self._from_drum_rack_to_simpler_notes()

        pitch = pitches[0]
        drum_pad = device.drum_pads[pitch]
        assert not drum_pad.is_empty, "the pitch '%s' corresponds to an empty drum pad" % pitch

        sample_path = drum_pad.chains[0].devices[0].sample.file_path
        ApplicationView.show_device()

        Backend.client().load_sample_in_simpler(sample_path)

        seq = Sequence()
        seq.wait_for_backend_event("sample_loaded")
        seq.add(partial(Backend.client().show_success, "Sample loaded"))
        return seq.done()

    def _from_drum_rack_to_simpler_notes(self) -> None:
        for clip in cast(SimpleMidiTrack, Song.selected_track()).clips:
            notes = clip.get_notes()
            for note in notes:
                note.pitch = 60

            clip.set_notes(notes)

    def clean_racks(self, track: Optional[SimpleTrack] = None) -> None:
        seq = Sequence()

        tracks = [track] if track is not None else Song.simple_tracks()

        for track in tracks:
            if not isinstance(track.instrument, InstrumentDrumRack):
                continue

            drum_rack = cast(DrumRackDevice, track.instrument.device)
            pads_count = len(drum_rack.filled_drum_pads)

            pitches = set(
                note.pitch for clip in track.clips for note in cast(MidiClip, clip).get_notes()
            )

            Logger.info("Treating track %s: %s pads" % (track, pads_count))
            if len(pitches) == 0:
                Logger.warning("No notes. Please remove the track")
            elif len(pitches) > 1:
                Logger.info("%s notes detected" % len(pitches))
                if pads_count > len(pitches):
                    Logger.warning("You can remove %s unused pads" % pads_count)
            else:
                Logger.info("1 note : converting to simpler")
                seq.add(track.select)
                seq.add(partial(self.drum_rack_to_simpler, track))
                seq.wait_ms(100)

        seq.done()
