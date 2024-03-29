import copy
import json
import os.path
from json.decoder import JSONDecodeError
from typing import Any, Dict

import fs.osfs


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

        pass

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

        name: str
        ser: Any
        value: Any

        f: fs.osfs.OSFS = fs.osfs.OSFS(os.path.dirname(file), create=True)

        if not f.exists(os.path.relpath(file, os.path.dirname(file))):
            return

        data: str = f.readtext(os.path.relpath(file, os.path.dirname(file)))

        f.close()

        try:
            ser = json.loads(data)
        except JSONDecodeError:
            return

        __dict__: Dict[str, Any] = super().__getattribute__("__dict__")

        for name, value in ser.items():

            if name not in __dict__["_configs"]:
                continue

            __dict__["_configs"][name] = value

    def save(self, file: str) -> None:

        config: Dict[str, Any] = copy.copy(
            super().__getattribute__("__dict__").get("_configs", {})
        )

        data: str = json.dumps(config, indent=2)

        f: fs.osfs.OSFS = fs.osfs.OSFS(os.path.dirname(file), create=True)

        f.writetext(os.path.relpath(file, os.path.dirname(file)), data)

        f.close()
