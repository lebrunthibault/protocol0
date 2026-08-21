import sys

import pytest

from protocol0.application.http.Router import get_routes
from protocol0.tests.domain.fixtures.p0 import make_protocol0, monkey_patch_static
from protocol0.tests.infra.scheduler.TickSchedulerSync import TickSchedulerSync

sys.dont_write_bytecode = True

# Global neutering of I/O (logs, backend client, http socket, undo): applied once,
# before any test module is imported. Was previously an import side effect of
# protocol0.tests.__init__.
monkey_patch_static()


@pytest.fixture
def tick_scheduler() -> TickSchedulerSync:
    return TickSchedulerSync()


@pytest.fixture
def p0(tick_scheduler: TickSchedulerSync):
    """A Protocol0 script wired against the LOM fakes, torn down after each test.

    Runs on the synchronous tick scheduler: nothing deferred executes until the
    test calls tick_scheduler.advance() / drain(). The route registry is
    snapshotted so plugin actions registered by one test don't leak into the next.
    """
    routes_snapshot = dict(get_routes())
    p0 = make_protocol0(tick_scheduler)
    yield p0
    p0.disconnect()
    routes = get_routes()
    routes.clear()
    routes.update(routes_snapshot)
