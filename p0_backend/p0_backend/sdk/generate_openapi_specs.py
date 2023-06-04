import inspect
import json
import os
from typing import Callable, Iterator

from apispec import APISpec
from loguru import logger
from openapi_spec_validator import validate_spec

from p0_backend.api.midi_server.routes import Routes

title = "P0 backend Client"
classname = "P0BackendClient"
out_folder = os.path.dirname(__file__)
package_name = "p0_backend_client"


def generate_openapi_specs():
    methods_dict = {}
    for name, method in Routes.__dict__.items():
        if not name.startswith("_"):
            methods_dict[name] = Routes

    methods = [getattr(cls, method_name) for method_name, cls in methods_dict.items()]
    spec = _generate_bare_spec(title=title)

    for method in methods:
        _add_spec_path_from_method(spec=spec, method=method)

    try:
        validate_spec(spec.to_dict())
        logger.info("spec is valid")
    except Exception as e:
        logger.error(e)
        return

    _write_to_file(
        folder_name=out_folder, spec=spec, package_name=package_name, classname=classname
    )


def _generate_bare_spec(title: str) -> APISpec:
    return APISpec(
        title=title,
        version="1.0.0",
        openapi_version="3.0.0",
        info=dict(description=title),
    )


def _add_spec_path_from_method(spec, method):
    # type: (APISpec, Callable) -> APISpec

    return spec.path(
        path="/%s" % method.__name__,
        parameters=list(_get_parameters_dict_from_method(method)),
        operations={
            "get": {"operationId": method.__name__, "responses": {"200": {"description": ""}}}
        },
    )


def _get_openapi_string_type(type_class):
    if type_class == str:
        return "string"
    if type_class == bool:
        return "boolean"
    elif type_class == int:
        return "integer"
    elif type_class == float:
        return "number"
    # NB : need to create a type schema for arrays
    # elif "list" in str(type_class).lower():
    #     return "array"
    else:
        return "object"


def _get_parameters_dict_from_method(method):
    # type: (Callable) -> Iterator
    signature = inspect.signature(method)
    parameters = signature.parameters.values()
    for param in parameters:
        if param.name in ("self", "cls"):
            continue
        param_spec = {
            "in": "query",
            "name": param.name,
            "required": param.default is param.empty,
            "schema": {"type": _get_openapi_string_type(param.annotation)},
        }
        if param.default is not param.empty:
            param_spec["schema"]["default"] = param.default
        if param == list(parameters)[-1]:
            param_spec["description"] = "last"

        yield param_spec


def _write_to_file(folder_name, spec, package_name, classname):
    # type: (str, APISpec, str, str) -> None
    with open("%s/openapi.yaml" % folder_name, "w") as f:
        f.write(spec.to_yaml())
    with open("%s/openapi_config.json" % folder_name, "w") as f:
        f.write(json.dumps({"packageName": package_name, "custom_classname": classname}))
    logger.info("wrote spec files %s" % folder_name)


if __name__ == "__main__":
    generate_openapi_specs()
