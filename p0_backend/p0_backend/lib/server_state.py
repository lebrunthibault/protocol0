from os.path import basename, dirname
from pathlib import Path
from typing import List, Dict, Union, Optional

from p0_backend.settings import Settings
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceEnumGroup import DeviceEnumGroup
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum
from pydantic import BaseModel

from p0_backend.lib.ableton_set import AbletonSet, AbletonSetManager, AbletonSetLight
import os
import glob

settings = Settings()


def list_sets() -> Dict[str, List[AbletonSetLight]]:
    top_folders = ["tracks", "paused", "palettes"]
    excluded_sets = ["Dancing Feet", "Backup", "_released"]
    ableton_sets = {}

    for top_folder in top_folders:
        top_folder_path = os.path.join(settings.ableton_set_directory, top_folder)
        ableton_sets[top_folder] = []

        assert os.path.exists(top_folder_path) and os.path.isdir(
            top_folder_path
        ), f"{top_folder} does not exist"
        als_files = glob.glob(os.path.join(top_folder_path, "**\\*.als"), recursive=True)

        for als_file in als_files:
            if any(word in als_file for word in excluded_sets):
                continue

            if top_folder != "palettes" and Path(als_file).stem != basename(dirname(als_file)):
                continue

            ableton_sets[top_folder].append(AbletonSetLight(path=als_file))

    return ableton_sets


class ServerState(BaseModel):
    active_set: Optional[AbletonSet]
    set_shortcuts: List[str]
    sample_categories: Dict[str, List[str]]
    favorite_device_names: List[List[Union[str, Dict]]]

    @classmethod
    def create(cls) -> "ServerState":
        def serialize_device_enum(d: Union[DeviceEnum, DeviceEnumGroup]) -> Union[str, Dict]:
            if isinstance(d, DeviceEnum):
                return d.name
            else:
                return d.to_dict()

        return ServerState(
            active_set=AbletonSetManager.active().dict() if AbletonSetManager.has_active_set() else None,
            set_shortcuts=["last", "default", "new"],
            sample_categories={
                category.name.lower(): category.subcategories
                for category in list(SampleCategoryEnum)
            },
            favorite_device_names=[
                list(map(serialize_device_enum, row)) for row in DeviceEnum.favorites()
            ],
        )
