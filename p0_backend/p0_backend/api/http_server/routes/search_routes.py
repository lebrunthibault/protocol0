from typing import List

import win32gui
from fastapi import APIRouter
import tkinter as tk
from threading import Timer

from loguru import logger

from p0_backend.lib.ableton.ableton import focus_ableton
from p0_backend.lib.notification import notify
from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import AbletonSetManager
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from protocol0.application.command.SelectTrackCommand import SelectTrackCommand

router = APIRouter()


@router.get("/track")
async def search_track() -> None:
    try:
        track_list = AbletonSetManager.active().current_state.track_names
    except Protocol0Error as e:
        notify(str(e))
        return

    if "Master" not in track_list:
        track_list.append("Master")

    root = tk.Tk()
    root.overrideredirect(True)
    try:
        win32gui.SetForegroundWindow(root.winfo_id())
    except Exception as e:
        logger.error(str(e))

    def autoclose() -> None:
        # noinspection PyBroadException
        try:
            if not entry.get():
                root.destroy()
        except Exception:
            pass

    autoclose_timer = Timer(10, autoclose)
    autoclose_timer.start()

    entry = tk.Entry(root, width=20)
    entry.focus()
    entry.pack()
    entry.bind("<Return>", (lambda event: get_input()))
    entry.bind("<Escape>", (lambda event: root.destroy()))

    def track_list_from_substring(value: str) -> List[str]:
        if value == "":
            return track_list

        data = []
        for item in track_list:
            if value.lower() in item.lower():
                data.append(item)

        return data

    def check_key(event) -> None:
        update_autocomplete(track_list_from_substring(event.widget.get()))

    entry.bind("<KeyRelease>", check_key)

    def update_autocomplete(data) -> None:
        # clear previous data
        lb.delete(0, "end")

        # put new data
        for item in data:
            lb.insert("end", item)

    lb = tk.Listbox(root)
    lb.pack()
    update_autocomplete(track_list)

    def onselect(evt) -> None:
        index = int(evt.widget.curselection()[0])
        submit(evt.widget.get(index))

    lb.bind("<Return>", onselect)
    lb.bind("<Double-1>", onselect)

    def get_input() -> None:
        submit(entry.get())

    def submit(track_name: str) -> None:
        # if input is partial, select the first track name in the list
        if track_name not in track_list:
            track_sub_list = track_list_from_substring(track_name)
            if track_sub_list:
                track_name = track_sub_list[0]

        p0_script_client().dispatch(SelectTrackCommand(track_name))

        autoclose_timer.cancel()

        focus_ableton()

        root.destroy()  # Close the window after getting the input

    root.mainloop()
