from typing import List, Dict, Union, Optional

from pydantic import BaseModel

from p0_backend.lib.ableton.ableton_set.ableton_set import AbletonSet
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import AbletonSetManager
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceEnumGroup import DeviceEnumGroup
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum


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
            active_set=AbletonSetManager.active() if AbletonSetManager.has_active_set() else None,
            set_shortcuts=["default", "new"],
            sample_categories={
                category.name.lower(): category.subcategories
                for category in list(SampleCategoryEnum)
            },
            favorite_device_names=[
                list(map(serialize_device_enum, row)) for row in DeviceEnum.favorites()
            ],
        )
