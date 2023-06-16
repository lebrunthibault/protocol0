from typing import List, Dict

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetImportInterface(object):
    _PRESET_CACHE: Dict[str, List[InstrumentPreset]] = {}

    def import_presets(self, use_cache: bool = True) -> List[InstrumentPreset]:
        cache_key = getattr(self, "_path", None)
        if use_cache and cache_key is not None and cache_key in self._PRESET_CACHE:
            return self._PRESET_CACHE[cache_key]
        else:
            presets = self._import_presets()
            if cache_key is not None:
                self._PRESET_CACHE[cache_key] = presets
            return presets

    def _import_presets(self) -> List[InstrumentPreset]:
        raise NotImplementedError
