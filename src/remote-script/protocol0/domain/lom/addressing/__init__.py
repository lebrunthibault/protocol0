"""Target addressing grammar of the action catalog (ClyphX-modeled).

Every action takes its targets as flat string params (`track="SEL"`,
`device="1.2.3"`, `value="TGL"`); these module-level resolvers turn a spec
into a domain object, raising Protocol0Warning with an explicit message on
failure (surfaced as a clean 500 by the http action executor).
"""
from protocol0.domain.lom.addressing.clip import resolve_clip  # noqa: F401
from protocol0.domain.lom.addressing.device import resolve_device  # noqa: F401
from protocol0.domain.lom.addressing.parameter import resolve_parameter  # noqa: F401
from protocol0.domain.lom.addressing.scene import resolve_scene  # noqa: F401
from protocol0.domain.lom.addressing.track import resolve_track  # noqa: F401
from protocol0.domain.lom.addressing.values import (  # noqa: F401
    resolve_adjustable,
    resolve_bool,
    resolve_continuous,
    resolve_quasi_continuous,
)
