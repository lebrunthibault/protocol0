from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface


class RecordProcessors(object):
    def __init__(
        self,
        pre_record: RecordProcessorInterface = None,
        record: RecordProcessorInterface = None,
        on_record_end: RecordProcessorInterface = None,
        post_record: RecordProcessorInterface = None,
        on_record_cancelled: RecordProcessorInterface = None,
    ) -> None:
        self.pre_record = pre_record
        self.record = record
        self.on_record_end = on_record_end
        self.post_record = post_record
        self.on_record_cancelled = on_record_cancelled

    def __repr__(self) -> str:
        # noinspection SpellCheckingInspection
        return (
            "RecordProcessors(\npre_record=%s,\nrecord=%s,\non_record_end=%s,\npost_record=%s,\non_record_cancelled=%s"
            % (
                self.pre_record,
                self.record,
                self.on_record_end,
                self.post_record,
                self.on_record_cancelled,
            )
        )

    def copy(self) -> "RecordProcessors":
        return RecordProcessors(
            pre_record=self.pre_record,
            record=self.record,
            on_record_end=self.on_record_end,
            post_record=self.post_record,
            on_record_cancelled=self.on_record_cancelled,
        )
