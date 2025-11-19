import json
import os
from typing import TypeVar, Generic
import typing as t

class CustomJSONEncoder(json.JSONEncoder):
    _custom_serializers = {}

    @staticmethod
    def register_serializer(type, serializer):
        CustomJSONEncoder._custom_serializers[type] = serializer

    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            if type(obj) in self._custom_serializers:
                return self._custom_serializers[type(obj)](obj)
            return str(obj)

K = TypeVar('K')
V = TypeVar('V')
class FiledDict(Generic[K, V]):
    """ Tries its best to mimick a json file, and reflect changes in file upon saving.
        Very useful for handling settings that need to be persistent
    """

    def __init__(self, file: str, autosave: bool = True, default: t.Dict[K, V] = {}):
        """ The file to mirror

        Args:
            file (string): path to the file
        """
        self.file = file
        self.autosave = autosave
        self.default = default
        if (not self.load()):
            self._settings = default
        self.save()
        self.type = type(self._settings)

    def __iter__(self):
        return iter(self._settings)

    def __len__(self):
        return len(self._settings)

    def __getitem__(self, name: K) -> V:
        return self._settings.__getitem__(name)

    def __setitem__(self, name: K, val: V):
        self._settings.__setitem__(name, val)
        if self.autosave:
            self.save()

    def __delitem__(self, key: K):
        self._settings.__delitem__(key)
        if self.autosave:
            self.save()

    def __getattr__(self, name):
        return getattr(self._settings, name)

    def save(self):
        if (self.file is not None):
            f = open(self.file,'w')
            f.write(json.dumps(self._settings, indent=4, cls=CustomJSONEncoder))

    def load(self):
        if (self.file is None):
            return False
        if os.path.isfile(self.file):
            f = open(self.file,'r')
            try:
                self._settings = json.load(f, cls=CustomJSONEncoder)
            except:
                self._settings = self.default
                self.save()
            finally:
                f.close()
            return True
        return False

    def keys(self) -> t.Iterable[K]:
        return self._settings.keys()

    def values(self) -> t.Iterable[V]:
        return self._settings.values()

    def items(self) -> t.Iterable[t.Tuple[K, V]]:
        return self._settings.items()

    def pop(self, key: K, if_fail: V = "") -> V:
        return self._settings.pop(key, if_fail)

    def remove(self, item: V) -> None:
        return self._settings.remove(item)

