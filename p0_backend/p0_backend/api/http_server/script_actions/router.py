import sys
from typing import List, Tuple
from unittest.mock import Mock

from fastapi import APIRouter
from pydantic import BaseModel
from protocol0.application.command.MidiNoteCommand import MidiNoteCommand

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.settings import Settings

router = APIRouter()

settings = Settings()


class Action(BaseModel):
    id: int
    name: str

    @classmethod
    def from_action(cls, action: Tuple[int, str]) -> "Action":
        return Action(id=action[0], name=action[1])


class ActionGroup(BaseModel):
    id: int
    name: str
    actions: List[Action]

    @classmethod
    def from_group_class(cls, group) -> "ActionGroup":
        return ActionGroup(
            id=group.CHANNEL,
            name=group.__module__.split(".")[-1].replace("ActionGroup", ""),
            actions=[Action.from_action(action) for action in group.actions],
        )


@router.get("", response_model=List[ActionGroup])
async def actions() -> List[ActionGroup]:
    sys.path.insert(0, f"{settings.project_directory}/protocol0_stub")

    from protocol0.application.control_surface import group
    from protocol0.domain.shared.utils.utils import import_package
    from protocol0.domain.shared.backend.Backend import Backend

    Backend._INSTANCE = Mock()
    from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

    import_package(group)

    action_group_classes = ActionGroupInterface.__subclasses__()

    for action_group_class in action_group_classes:
        action_group_class.actions = []
        ActionGroupInterface.add_encoder = (
            lambda self, identifier, name, **k: action_group_class.actions.append(
                (identifier, name)
            )
        )

        action_group = action_group_class(Mock(), Mock())
        action_group.configure()

    return sorted(
        [ActionGroup.from_group_class(group) for group in action_group_classes], key=lambda g: g.id
    )


@router.get("/{group_id}/{action_id}")
async def execute_action(group_id: int, action_id: int):
    p0_script_client().dispatch(MidiNoteCommand(group_id, action_id))

    return "ok"
