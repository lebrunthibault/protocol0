import ctypes
import queue
import tkinter as tk
from threading import Timer, Thread
from typing import List, Optional

from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import focus_ableton
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import AbletonSetManager
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.keys import send_keys
from p0_backend.lib.notification import notify
from p0_backend.lib.window.window import focus_window_by_handle
from protocol0.application.command.SelectTrackCommand import SelectTrackCommand

router = APIRouter()
thread: Optional[Thread] = None
track_list_search_history: set[str] = set()
task_queue = queue.Queue()


@router.get("/track")
async def _search_track() -> None:
    from loguru import logger

    logger.success("search")
    _create_thread()
    task_queue.put("show_window")


def _create_thread() -> None:
    global thread

    if thread:
        return None

    thread = Thread(target=search_track)
    thread.daemon = True
    thread.start()


def _get_search_window() -> tk.Tk:
    root = tk.Tk()
    w = 160  # width for the Tk root
    h = 450  # height for the Tk root

    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    # set the dimensions of the screen
    # and where it is placed
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    root.overrideredirect(True)
    root.bind("<Escape>", (lambda event: root.withdraw()))

    focus_window_by_handle(root.winfo_id())

    return root


def search_track() -> None:
    try:
        track_list = AbletonSetManager.active().current_state.track_names
    except Protocol0Error as e:
        notify(str(e))
        return

    if "Master" not in track_list:
        track_list.append("Master")

    root = _get_search_window()

    def autoclose() -> None:
        # noinspection PyBroadException
        try:
            if not entry.get():
                root.withdraw()
        except Exception:
            pass

    autoclose_timer = Timer(10, autoclose)
    autoclose_timer.start()

    entry = tk.Entry(root, width=20, font=("Arial", 12))

    entry.focus()
    entry.pack()
    entry.bind("<Return>", (lambda event: get_input()))
    entry.bind("<Escape>", (lambda event: root.withdraw()))

    def track_list_from_substring(value: str) -> List[str]:
        if value == "":
            if AbletonSetManager.SELECTED_TRACKS_HISTORY:
                return AbletonSetManager.SELECTED_TRACKS_HISTORY
            else:
                return track_list

        data = []
        for item in track_list:
            if item.lower().startswith(value.lower()):
                data.append(item)

        return data

    def check_key(event) -> None:
        update_autocomplete(track_list_from_substring(event.widget.get()))

    entry.bind("<KeyRelease>", check_key)

    def update_autocomplete(data) -> None:
        # clear previous data
        list_box.delete(0, "end")

        # put new data
        for item in data:
            list_box.insert("end", item)

    list_box = tk.Listbox(root, height=20, font=("Arial", 12))
    list_box.pack()
    update_autocomplete(track_list)

    def on_select(evt) -> None:
        index = int(evt.widget.curselection()[0])
        submit(evt.widget.get(index))

    list_box.bind("<Return>", on_select)
    list_box.bind("<Double-1>", on_select)

    def on_down(_) -> None:
        if not list_box.curselection():
            send_keys("{TAB}")

    list_box.bind_all("<Down>", on_down)

    def on_tab(_) -> str:
        send_keys("{DOWN}")
        return "break"

    list_box.bind("<Tab>", on_tab)

    def get_input() -> None:
        submit(entry.get())

    def submit(track_name: str) -> None:
        # if input is partial, select the first track name in the list
        if track_name not in track_list:
            track_sub_list = track_list_from_substring(track_name)
            if track_sub_list:
                track_name = track_sub_list[0]

        track_list_search_history.add(track_name)
        p0_script_client().dispatch(SelectTrackCommand(track_name))

        autoclose_timer.cancel()

        focus_ableton()

        root.withdraw()  # Close the window after getting the input

    set_to_foreground = ctypes.windll.user32.SetForegroundWindow
    keybd_event = ctypes.windll.user32.keybd_event
    alt_key = 0x12
    extended_key = 0x0001
    key_up = 0x0002

    def steal_focus():
        keybd_event(alt_key, 0, extended_key | 0, 0)
        set_to_foreground(root.winfo_id())
        keybd_event(alt_key, 0, extended_key | key_up, 0)

        entry.focus_set()

    def check_queue():
        try:
            task = task_queue.get_nowait()
            if task == "show_window":
                root.deiconify()

                from loguru import logger

                logger.success("shown")
                update_autocomplete(track_list_from_substring(""))
                entry.delete(0, tk.END)
                steal_focus()

        except queue.Empty:
            pass

        root.after(5, check_queue)

    check_queue()
    tk.mainloop()
    # root.mainloop()
