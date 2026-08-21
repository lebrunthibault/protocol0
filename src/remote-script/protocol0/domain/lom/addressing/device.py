from typing import TYPE_CHECKING, List

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning

if TYPE_CHECKING:
    from protocol0.domain.lom.device.Device import Device
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


def resolve_device(track: "SimpleTrack", spec: str = "SEL") -> "Device":
    """Resolves a device spec on a track.

    Specs: SEL (the track's selected device, default) | 1-based top-level
    index ("2") | dotted rack path "1.2.3" (3rd device of the 2nd chain of
    the 1st rack — pairs of chain.device indexes may nest deeper) | bare or
    quoted name over all devices incl. rack chains (exact, then substring).
    """
    spec = (spec or "SEL").strip()

    if spec.upper() in ("SEL", ""):
        selected = track.devices.selected
        if selected is None:
            raise Protocol0Warning("no selected device on '%s'" % track.name)
        return selected

    top_level: List["Device"] = list(track.devices)

    if spec.isdigit():
        index = int(spec)
        if not 1 <= index <= len(top_level):
            raise Protocol0Warning(
                "no device %s on '%s' (%d devices)" % (spec, track.name, len(top_level))
            )
        return top_level[index - 1]

    if all(part.isdigit() for part in spec.split(".")) and "." in spec:
        return _resolve_dotted(track, spec, top_level)

    name = spec[1:-1] if spec.startswith('"') and spec.endswith('"') and len(spec) > 1 else spec
    devices = track.devices.all
    exact = [d for d in devices if d.name and d.name.lower().strip() == name.lower().strip()]
    if exact:
        return exact[0]
    if not spec.startswith('"'):
        partial = [d for d in devices if d.name and name.lower().strip() in d.name.lower()]
        if partial:
            return partial[0]

    raise Protocol0Warning(
        "no device matching '%s' on '%s' (devices: %s)"
        % (spec, track.name, ", ".join(d.name for d in devices))
    )


def _resolve_dotted(track: "SimpleTrack", spec: str, top_level: List["Device"]) -> "Device":
    """Walks a ClyphX-style dotted rack path: first index is a top-level device,
    then (chain, device) index pairs descend into racks."""
    from protocol0.domain.lom.device.RackDevice import RackDevice

    parts = [int(part) for part in spec.split(".")]
    if len(parts) % 2 == 0:
        raise Protocol0Warning(
            "invalid device path '%s': expected rack.chain.device index pairs" % spec
        )

    if not 1 <= parts[0] <= len(top_level):
        raise Protocol0Warning(
            "no device %d on '%s' (%d devices)" % (parts[0], track.name, len(top_level))
        )
    device = top_level[parts[0] - 1]

    for chain_index, device_index in zip(parts[1::2], parts[2::2]):
        if not isinstance(device, RackDevice):
            raise Protocol0Warning("'%s' is not a rack (path '%s')" % (device.name, spec))
        if not 1 <= chain_index <= len(device.chains):
            raise Protocol0Warning(
                "no chain %d in '%s' (%d chains)" % (chain_index, device.name, len(device.chains))
            )
        chain = device.chains[chain_index - 1]
        if not 1 <= device_index <= len(chain.devices):
            raise Protocol0Warning(
                "no device %d in chain %d of '%s' (%d devices)"
                % (device_index, chain_index, device.name, len(chain.devices))
            )
        device = chain.devices[device_index - 1]

    return device
