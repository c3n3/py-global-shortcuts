from typing import Callable
from . import globals as g
from . filed_dict import FiledDict
import os

class Binding:
    def __init__(self, shortcut: str, function: Callable):
        self.shortcut = shortcut
        self.function: Callable = function

    def __repr__(self):
        return f"Binding({self.shortcut}, {self.function})"

    def __str__(self):
        return self.__repr__()

class ShortcutBinder:
    def __init__(self):
        self.shortcuts: FiledDict[str, Binding] = FiledDict(g.cache_file, autosave=True, default={})

    def add_binding(self, shortcut, function):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_current_bindings(self) -> list[Binding]:
        return list(self.shortcuts.values())

    def remove_binding(self, shortcut: str):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def cleanup(self):
        """Cleanup resources if needed."""
        pass

    def _deregister_shortcut(self, shortcut: str):
        if shortcut in self.shortcuts:
            del self.shortcuts[shortcut]

    def _register_shortcut(self, shortcut: str, function: Callable):
        self.shortcuts[shortcut] = Binding(shortcut, function)

    def handle_shortcut(self, shortcut: str):
        if shortcut in self.shortcuts:
            self.shortcuts[shortcut].function()
        else:
            print(f"No function registered for shortcut: {shortcut}")
