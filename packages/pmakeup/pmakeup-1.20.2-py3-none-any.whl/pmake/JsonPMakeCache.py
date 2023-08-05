import json
import os
from typing import Any, Dict, Iterable

from pmakeup.IPMakeupCache import IPMakeupCache
from pmakeup.commons_types import path


class JsonPMakeupCache(IPMakeupCache):

    def __init__(self, file_path: path):
        self.file_path: path = file_path
        self.d: Dict[str, Any] = {}
        # load the cache (if present)
        if self.is_cache_present():
            with open(self.file_path, "r", encoding="utf-8") as f:
                json_string = f.read()
            self.d: Dict[str, Any] = json.loads(json_string)

    def reset(self):
        self.d.clear()
        self.update_cache()

    def is_empty(self) -> bool:
        return len(self.d) == 0

    def variable_names(self) -> Iterable[str]:
        yield from self.d.keys()

    def is_cache_present(self) -> bool:
        return os.path.exists(self.file_path)

    def get_name(self) -> str:
        return f"JSON Cache at {os.path.abspath(self.file_path)}"

    def set_variable_in_cache(self, name: str, value: Any, overwrites_is_exists: bool = True):
        if overwrites_is_exists is False and name in self.d:
            raise KeyError(f"variable \"{name}\" already exists in the cache {self.get_name()}")
        self.d[name] = value

    def get_variable_in_cache(self, name: str) -> Any:
        return self.d[name]

    def has_variable_in_cache(self, name: str) -> bool:
        return name in self.d

    def update_cache(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.d,
                check_circular=True,
                indent=4,
                sort_keys=True,
            ))
