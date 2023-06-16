from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentActivatedEvent(object):
    def __init__(self, instrument: InstrumentInterface) -> None:
        self.instrument = instrument
