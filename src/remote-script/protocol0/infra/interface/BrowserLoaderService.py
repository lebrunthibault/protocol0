import Live
from typing import Dict

from protocol0.domain.lom.device.DeviceCategories import (
    _AUDIO_FX_LOWER,
    _INSTRUMENTS_LOWER,
    _MIDI_FX_LOWER,
)
from protocol0.domain.lom.device.Sample.BrowserItemNotFoundError import BrowserItemNotFoundError
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.logging.Logger import Logger


class BrowserLoaderService(object):
    def __init__(self, browser: Live.Browser.Browser) -> None:
        self._browser = browser
        self._cached_browser_items: Dict[str, Dict[str, Live.Browser.BrowserItem]] = {}

    def load_device(self, device_name: str) -> None:
        """Loads a built-in Live device. Matching is case-insensitive."""
        name_lower = device_name.lower()
        if name_lower in _MIDI_FX_LOWER:
            self._do_load_item(self._get_item_for_category("midi_effects", device_name))
        elif name_lower in _INSTRUMENTS_LOWER:
            self._do_load_item(self._get_item_for_category("instruments", device_name))
        elif name_lower in _AUDIO_FX_LOWER:
            self._do_load_item(self._get_item_for_category("audio_effects", device_name))
        else:
            item = self._get_item_for_category("plugins", device_name)

            if item is None:
                raise Protocol0Warning("Couldn't load %s" % device_name)

            self._do_load_item(item, "Plugin")

    def load_sample(self, name: str) -> None:
        """Loads items from the sample category."""
        self._do_load_item(self._get_item_for_category("samples", name), "Sample")

    def load_from_user_library(self, name: str) -> None:
        """Loads items from the user library category"""
        self._do_load_item(self._get_item_for_category("user_library", name), "from User Library")

    def _do_load_item(self, item: Live.Browser.BrowserItem, header: str = "Device") -> None:
        """Handles loading an item and displaying load info in status bar."""
        # NB : activating this will hotswap drum rack pads if a drum rack is selected
        # ApplicationView.toggle_browse()
        if item and item.is_loadable:
            Logger.info("Loading %s: %s" % (header, item.name))
            # noinspection PyArgumentList
            self._browser.load_item(item)
            # ApplicationView.toggle_browse()
            # Scheduler.defer(partial(self._browser.load_item, item))
        else:
            raise Protocol0Error("Couldn't load %s item" % header)

    def _get_item_for_category(self, category: str, name: str) -> Live.Browser.BrowserItem:
        """Returns the cached item for the category. Matching is case-insensitive."""
        self._cache_category(category)
        items = self._cached_browser_items[category]
        item = items.get(name, None)
        if item is None:
            name_lower = name.lower()
            item = next(
                (i for key, i in items.items() if key.lower() == name_lower), None
            )
        if item is None:
            raise BrowserItemNotFoundError(name)

        return item

    def _cache_category(self, category: str) -> None:
        """This will cache an entire dict of items for the category if one doesn't
        already exist."""
        if category == "user_library" and self._cached_browser_items.get(category, False):
            self._cached_browser_items[category] = {}
        if not self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
            self._get_children_for_item(
                getattr(self._browser, category), self._cached_browser_items[category]
            )

    def _get_children_for_item(
        self,
        item: Live.Browser.BrowserItem,
        i_dict: Dict[str, Live.Browser.BrowserItem],
        is_drum_rack: bool = False,
    ) -> None:
        """Recursively builds dict of children items for the given item. This is needed
        to deal with children that are folders. If is_drum_rack, will only deal with
        racks in the root (not drum hits)."""
        for i in item.iter_children:
            if i.is_folder or not i.is_loadable:
                if is_drum_rack:
                    continue
                self._get_children_for_item(i, i_dict)
            elif not is_drum_rack or i.name.endswith(".adg"):
                i_dict[i.name] = i
