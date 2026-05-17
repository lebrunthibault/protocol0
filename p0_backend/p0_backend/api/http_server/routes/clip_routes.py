from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from p0_backend.lib.midi.analyze_key import analyze_key, NoteModel

router = APIRouter()


class NotesModel(BaseModel):
    notes: List[NoteModel]


@router.post("/analyze_key")
async def _analyze_key(notes: NotesModel):
    analyze_key(notes.notes)
