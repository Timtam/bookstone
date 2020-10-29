import copy
import json
import os.path
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, TextIO

from py_singleton import singleton

from library.naming_scheme import NamingScheme


@singleton
class ConfigurationManager:
    def __init__(self) -> None:

        __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

        __dict__["_configs"] = {}

        # configure default values
        self.init()

    def _add(self, key: str, value: Any) -> None:

        __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

        __dict__["_configs"][key] = value

    def init(self) -> None:

        self._add(
            "namingSchemes",
            [
                NamingScheme(
                    name="Default 1",
                    standalone="{author} - {title}",
                    volume="{author} - {series}/{number} - {title}",
                    default=True,
                )
            ],
        )

    def __getattribute__(self, name: str) -> Any:

        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

        if name in __dict__["_configs"]:
            return __dict__["_configs"][name]

        raise AttributeError(
            "ConfigurationManager object has no attribute '{name}'".format(name=name)
        )

    def __setattr__(self, name: str, value: Any) -> None:

        __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

        try:
            if name not in __dict__["_configs"]:
                raise AttributeError(
                    "ConfigurationManager object has no attribute '{name}'".format(
                        name=name
                    )
                )

            __dict__["_configs"][name] = value

        except KeyError:
            # accessed before initialization -> py_singleton
            __dict__[name] = value

    def load(self, file: str) -> None:

        f: TextIO
        name: str
        value: Any

        if not os.path.exists(file):
            return

        with open(file, "r") as f:
            data: str = f.read()

            ser: Any

            try:
                ser = json.loads(data)
            except JSONDecodeError:
                return

            __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

            for name, value in ser.items():

                if name not in __dict__["_configs"]:
                    continue

                if name == "namingSchemes":

                    scheme: Dict[str, str]

                    for scheme in value:

                        __dict__["_configs"][name].append(NamingScheme(**scheme))  # type: ignore

                else:
                    __dict__["_configs"][name] = value

    def save(self, file: str) -> None:

        config: Dict[str, Any] = copy.copy(
            super().__getattribute__("__dict__").get("_configs", {})
        )
        f: TextIO

        # preparing configuration by handling any special cases beforehand

        schemes: List[Dict[str, str]] = []
        scheme: NamingScheme

        for scheme in config.get("namingSchemes", []):
            if not scheme.default:
                schemes.append(scheme.serialize())

        config["namingSchemes"] = schemes

        data: str = json.dumps(config, indent=2)

        with open(file, "w") as f:
            f.write(data)
