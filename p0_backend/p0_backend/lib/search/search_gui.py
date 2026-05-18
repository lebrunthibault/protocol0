import queue
import tkinter as tk
from threading import Timer, Thread
from typing import List, Optional

from loguru import logger

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import focus_ableton
from p0_backend.lib.ableton.ableton_set.ableton_set import AbletonTrack
from p0_backend.lib.search.search_queue import search_queue
from p0_backend.lib.window.window import focus_window_by_handle, focus_tkinter_window

thread: Optional[Thread] = None
track_list_search_history: set[str] = set()
selected_track: Optional[str] = None


def create_thread(reset: bool) -> None:
    global thread

    if thread:
        if reset:
            search_queue.put("stop")
            thread.join()
        else:
            return None

    thread = Thread(target=search_track)
    thread.daemon = True
    thread.start()


def get_selected_index(event: tk.Event):
    return int(event.widget.curselection()[0])


class SearchBox:
    def __init__(self):
        self.root = _get_search_window()

        self._tracks: List[AbletonTrack] = []
        self._selection_history: List[AbletonTrack] = []
        self._autoclose_timer = None

        self._entry = tk.Entry(self.root, width=20, font=("Arial", 12))

        self._entry.focus()
        self._entry.pack()
        self._entry.bind("<Return>", (lambda event: get_input()))
        self._entry.bind("<Escape>", (lambda event: self.root.withdraw()))

        self._list_box = tk.Listbox(
            self.root,
            selectmode="browse",
            height=20,
            font=("Arial", 12),
            activestyle="dotbox",
            selectborderwidth=4,
            borderwidth=0,
            relief="flat",
        )

        self._list_box.pack()

        self._entry.bind("<KeyRelease>", self.on_key_press)

        self._list_box.bind("<Return>", self.on_select)
        self._list_box.bind("<space>", self.on_select)
        self._list_box.bind("<Double-1>", self.on_select)

        self._list_box.bind_all("<Down>", self.on_tab)

        self._entry.bind("<Tab>", self.on_entry_tab)
        self._list_box.bind("<Tab>", self.on_tab)

        def get_input() -> None:
            self.submit(self._entry.get())

    def _refresh_tracks(self) -> None:
        """Pull the current set state from the script and refresh the local
        track list. Selection history entries that no longer match a track
        are dropped (track might have been renamed/removed)."""
        try:
            state = p0_script_client().get_set_state()
        except Exception as e:
            logger.warning(f"get_set_state failed: {e}")
            self._tracks = []
            return

        self._tracks = [AbletonTrack(**t) for t in state["tracks"]]
        track_names = {t.name for t in self._tracks}
        self._selection_history = [t for t in self._selection_history if t.name in track_names]

    def _filter(self, search: str) -> List[AbletonTrack]:
        if search == "":
            if len(self._selection_history) > 1:
                # hide currently selected track
                return self._selection_history[1:]
            else:
                return self._tracks

        return [t for t in self._tracks if search.lower() in t.name.lower()]

    def _init_autoclose(self):
        if self._autoclose_timer:
            self._autoclose_timer.cancel()

        def autoclose() -> None:
            # noinspection PyBroadException
            try:
                if not self._entry.get():
                    self.root.withdraw()
            except Exception:
                pass

        self._autoclose_timer = Timer(10, autoclose)
        self._autoclose_timer.start()

    def on_key_press(self, event) -> None:
        self.update_search_results(self._filter(event.widget.get()))
        self._init_autoclose()

    def on_entry_tab(self, _: tk.Event) -> None:
        self._list_box.selection_set(0)

    def on_tab(self, event: tk.Event) -> str:
        selected_index = get_selected_index(event)
        self._list_box.selection_clear(0, tk.END)

        if event.state == 9:  # shift tab
            if selected_index == 0:
                return ""  # don't block tab key
            self._list_box.selection_set(selected_index - 1)
        else:
            if selected_index < self._list_box.index(tk.END) - 1:
                selected_index += 1

            self._list_box.selection_set(selected_index)

        self._init_autoclose()

        return "break"

    def on_select(self, evt: tk.Event) -> None:
        self.submit(evt.widget.get(get_selected_index(evt)))

    def show(self) -> None:
        self._refresh_tracks()
        self.root.deiconify()
        self.update_search_results(self._filter(""))
        self._entry.delete(0, tk.END)
        focus_tkinter_window(self.root)
        self._entry.focus_set()

    def update_search_results(self, tracks: List[AbletonTrack]) -> None:
        # clear previous data
        self._list_box.delete(0, "end")

        # put new data
        for i, track in enumerate(tracks):
            self._list_box.insert("end", track.name)
            self._list_box.itemconfig(i, {"bg": track.rgb_color})

    def submit(self, track_name: str) -> None:
        # if input is partial, select the first track name in the list
        if track_name not in [t.name for t in self._tracks]:
            track_sub_list = self._filter(track_name)
            if track_sub_list:
                track_name = track_sub_list[0].name

        track_list_search_history.add(track_name)
        try:
            p0_script_client().select_track(track_name)
        except Exception as e:
            logger.warning(f"select_track failed: {e}")

        # Local selection history (last selected first, deduped).
        track = next((t for t in self._tracks if t.name == track_name), None)
        if track is not None and track.name.lower() != "master":
            self._selection_history = [t for t in self._selection_history if t.name != track.name]
            self._selection_history.insert(0, track)

        if self._autoclose_timer:
            self._autoclose_timer.cancel()  # type: ignore[unreachable]

        focus_ableton()

        self.root.withdraw()  # Close the window after getting the input

    def destroy(self) -> None:
        self.root.destroy()


def _get_search_window() -> tk.Tk:
    root = tk.Tk()
    w = 160  # width for the Tk root
    h = 450  # height for the Tk root

    # get screen width and height
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = 1500
    y = (hs / 2) - (h / 2)

    # set the dimensions of the screen
    # and where it is placed
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    root.overrideredirect(True)
    root.bind("<Escape>", (lambda event: root.withdraw()))

    focus_window_by_handle(root.winfo_id())

    return root


def search_track() -> None:
    search_box = SearchBox()
    logger.success(search_box)

    def check_queue():
        try:
            task = search_queue.get_nowait()
            if task == "show_window":
                search_box.show()
            elif task == "stop":
                search_box.destroy()
                return

        except queue.Empty:
            pass

        search_box.root.after(5, check_queue)

    check_queue()
    tk.mainloop()
