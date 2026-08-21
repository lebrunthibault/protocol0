from typing import TYPE_CHECKING

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning

if TYPE_CHECKING:
    from protocol0.domain.lom.device.Device import Device
    from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


def resolve_parameter(device: "Device", spec: str) -> "DeviceParameter":
    """Resolves a parameter spec on a device.

    Specs: 1-based index ("2", Live's parameter order) | bare or quoted name
    (exact, then substring).
    """
    spec = (spec or "").strip()
    parameters = device.parameters

    if spec.isdigit():
        index = int(spec)
        if not 1 <= index <= len(parameters):
            raise Protocol0Warning(
                "no parameter %s on '%s' (%d parameters)" % (spec, device.name, len(parameters))
            )
        return parameters[index - 1]

    name = spec[1:-1] if spec.startswith('"') and spec.endswith('"') and len(spec) > 1 else spec
    exact = [p for p in parameters if p.name.lower().strip() == name.lower().strip()]
    if exact:
        return exact[0]
    if not spec.startswith('"'):
        partial = [p for p in parameters if name.lower().strip() in p.name.lower()]
        if partial:
            return partial[0]

    raise Protocol0Warning(
        "no parameter matching '%s' on '%s' (parameters: %s)"
        % (spec, device.name, ", ".join(p.name for p in parameters))
    )
