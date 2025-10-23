from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from p0_backend.lib.midi.analyze_key import analyze_key, NoteModel

from protocol0.application.command.CleanLoopCommand import (
    CleanLoopCommand,
)
from protocol0.application.command.LoopSelectedClipCommand import LoopSelectedClipCommand
from protocol0.application.command.MoveClipLoopCommand import MoveClipLoopCommand
from protocol0.application.command.RemoveMutedNotesCommand import (
    RemoveMutedNotesCommand,
)
from protocol0.application.command.SetClipLoopLengthCommand import SetClipLoopLengthCommand
from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand

from p0_backend.api.client.p0_script_api_client import p0_script_client

router = APIRouter()


class NotesModel(BaseModel):
    notes: List[NoteModel]


@router.get("/toggle_notes")
async def _toggle_clip_notes():
    p0_script_client().dispatch(ToggleNotesCommand())


@router.get("/loop_selected")
async def loop_selected():
    p0_script_client().dispatch(LoopSelectedClipCommand())


@router.get("/move_loop")
async def move_loop(forward: bool = True, bar: bool = False):
    p0_script_client().dispatch(MoveClipLoopCommand(forward=forward, bar=bar))


@router.get("/set_loop_length")
async def set_loop_length(bar_length: int):
    p0_script_client().dispatch(SetClipLoopLengthCommand(bar_length=bar_length))


@router.get("/clean_arrangement_loop")
async def clean_arrangement_loop():
    p0_script_client().dispatch(CleanLoopCommand())


@router.get("/clear_muted_notes")
async def clear_muted_notes():
    p0_script_client().dispatch(RemoveMutedNotesCommand())


@router.post("/analyze_key")
async def _analyze_key(notes: NotesModel):
    analyze_key(notes.notes)
