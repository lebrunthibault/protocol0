from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.shared.sequence.Sequence import Sequence


def test_sanity_checks() -> None:
    seq = Sequence()
    seq.add([])
    seq.done()
    assert seq.state.terminated


def test_async() -> None:
    test_res = []
    seq = Sequence()
    seq.defer()
    seq.add(lambda: test_res.append(4), name="add 4")
    seq.done()

    assert test_res == []


def test_wait_for_event():
    test_res = []

    seq = Sequence()
    seq.wait_for_event(BarEndingEvent)
    seq.add(lambda: test_res.append(False), name="appending res seq 1")
    seq.done()

    assert test_res == []
    seq._cancel()

    seq2 = Sequence()
    seq2.wait_for_event(BarEndingEvent)
    seq2.add(lambda: test_res.append(True), name="appending res seq 2")
    seq2.done()

    DomainEventBus.emit(BarEndingEvent())

    assert test_res == [True]


def test_wait_for_event_match():
    test_res = []

    class TestEvent(object):
        def __init__(self, value: int) -> None:
            self.value = value

        def target(self) -> int:
            return self.value

    seq = Sequence()
    seq.wait_for_event(TestEvent, 2)
    seq.add(lambda: test_res.append(True), name="appending res seq 2")
    seq.done()

    DomainEventBus.emit(TestEvent(1))

    assert test_res == []
    DomainEventBus.emit(TestEvent(2))
    assert test_res == [True]
    seq._cancel()


def test_cancel():
    test_res = []
    seq = Sequence()
    seq.add(seq._cancel)
    seq.add(lambda: test_res.append(True))
    seq.done()

    assert test_res == []
