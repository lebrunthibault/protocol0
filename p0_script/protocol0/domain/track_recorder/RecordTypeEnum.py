from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class RecordTypeEnum(AbstractEnum):
    MIDI = "Midi"
    MIDI_OVERWRITE = "Midi overwrite"
    MIDI_RESAMPLE = "Midi resample"
    MIDI_UNLIMITED = "Midi unlimited"
    AUDIO = "Audio"
    AUDIO_FULL = "Audio full"
    AUDIO_MULTI_SCENE = "Audio multi scene"

    @property
    def records_midi(self) -> bool:
        return self in (
            RecordTypeEnum.MIDI,
            RecordTypeEnum.MIDI_OVERWRITE,
            RecordTypeEnum.MIDI_RESAMPLE,
            RecordTypeEnum.MIDI_UNLIMITED,
        )

    def get_count_in(self) -> CountInInterface:
        from protocol0.domain.track_recorder.count_in.CountInOneBar import CountInOneBar
        from protocol0.domain.track_recorder.count_in.CountInShort import CountInShort

        if self.records_midi:
            return CountInOneBar()
        else:
            return CountInShort()

    @property
    def speed_up_record(self) -> bool:
        return self == RecordTypeEnum.MIDI_OVERWRITE

    @property
    def has_solo_count_in(self) -> bool:
        return self != RecordTypeEnum.MIDI_OVERWRITE

    @property
    def clear_clips(self) -> bool:
        return self != RecordTypeEnum.MIDI_OVERWRITE

    @property
    def delete_clips(self) -> bool:
        return self not in (RecordTypeEnum.MIDI_OVERWRITE, RecordTypeEnum.MIDI_RESAMPLE)
