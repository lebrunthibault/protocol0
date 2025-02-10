from enum import Enum

from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface


class RecordTypeEnum(Enum):
    MIDI = "Midi"
    MIDI_OVERWRITE = "Midi overwrite"
    MIDI_RESAMPLE = "Midi resample"
    AUDIO = "Audio"

    @property
    def records_midi(self) -> bool:
        return self in (
            RecordTypeEnum.MIDI,
            RecordTypeEnum.MIDI_OVERWRITE,
            RecordTypeEnum.MIDI_RESAMPLE,
        )

    def get_count_in(self) -> CountInInterface:
        from protocol0.domain.track_recorder.count_in.CountInOneBar import CountInOneBar
        from protocol0.domain.track_recorder.count_in.CountInShort import CountInShort

        if self.records_midi:
            return CountInOneBar()
        else:
            return CountInShort()

    @property
    def has_solo_count_in(self) -> bool:
        return self != RecordTypeEnum.MIDI_OVERWRITE

    @property
    def clear_clips(self) -> bool:
        return self != RecordTypeEnum.MIDI_OVERWRITE

    @property
    def delete_clips(self) -> bool:
        return self not in (
            RecordTypeEnum.MIDI_OVERWRITE,
            RecordTypeEnum.MIDI_RESAMPLE,
            RecordTypeEnum.AUDIO,
        )

    @property
    def should_quantize(self) -> bool:
        return self == RecordTypeEnum.MIDI
