import sys
from os.path import dirname
from unittest.mock import Mock

sys.path.insert(0, f"{dirname(__file__)}/protocol0_stub")

from protocol0.application.Protocol0 import Protocol0
from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.track.routing.RoutingTrackDescriptor import RoutingTrackDescriptor
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.func import nop
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.shared.Undo import Undo
from protocol0.shared.logging.Logger import Logger
from protocol0.tests.domain.fixtures.song import AbletonSong
from protocol0.tests.infra.scheduler.TickSchedulerTest import TickSchedulerTest


def make_protocol0() -> Protocol0:
    live_song = AbletonSong()
    Protocol0.song = lambda _: live_song
    wait = Scheduler.wait
    Scheduler.wait = classmethod(nop)
    monkey_patch_static()
    p0 = Protocol0(Mock())
    Scheduler(TickSchedulerTest(), BeatScheduler(live_song))
    Scheduler.wait = wait
    return p0


def monkey_patch_static():
    # hide logs
    Logger(LoggerService())
    Logger.dev = classmethod(nop)
    Logger.info = classmethod(nop)
    Logger.warning = classmethod(nop)

    Backend(nop)
    Undo(nop, nop)
    AbletonSet.notify = nop
    # noinspection PyTypeChecker
    Scheduler(TickSchedulerTest(), None)  # ignore beat scheduling in tests

    # remove this until fixtures are thorough
    ActionGroupFactory.create_action_groups = classmethod(nop)

    RoutingTrackDescriptor.__set__ = nop

    def log(_, message, *__, **___):
        print(message)

    Logger._log = classmethod(log)
