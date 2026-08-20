"""Record actions — resampling the selected track.

Single-file drop-in plugin (no package, no ``__init__.py``), like
``DevicePlugin``. It exposes ``POST /api/action/record/resample_selected_track``,
which delegates to :class:`RecordService`, so the action shows up in the agent's
action catalog and is bindable to a shortcut like any other action.
"""
from typing import Optional

from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.shared.sequence.Sequence import Sequence


class RecordPlugin(PluginInterface):
    name = "record"

    @action
    def resample_selected_track(self) -> Optional[Sequence]:
        """Resample the selected track into an audio track routed from it."""
        # Returned so ``@action`` closes the undo step only once recording is done.
        return get_container().get(RecordService).resample_selected_track()
