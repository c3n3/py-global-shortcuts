import re
from . import utilities as u
from . import shortcut_binder as sb
from . import globals as g
from typing import Union
import subprocess
import pynput

class PynputBinder(sb.KeyBinder):
    def __init__(self):
        self._hotkeys: dict[str, pynput.keyboard.HotKey] = {}
        self._key_listener = pynput.keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._key_listener.start()
        super().__init__()


    def _on_press(self, key):
        can = self._key_listener.canonical(key)
        for hotkey in self._hotkeys.values():
            hotkey.press(can)


    def _on_release(self, key):
        can = self._key_listener.canonical(key)
        for hotkey in self._hotkeys.values():
            hotkey.release(can)


    def _deregister_key_binding(self, shortcut: str):
        if shortcut in self._hotkeys:
            del self._hotkeys[shortcut]        


    def cleanup(self):
        self._key_listener.stop()


    def _create_hotkey_fun(self, shortcut: str):
        def fun():
            self.handle_shortcut(shortcut)
        return fun


    def _register_key_binding(self, shortcut):
        if shortcut in self._hotkeys:
            return
        keys = pynput.keyboard.HotKey.parse(shortcut)
        for i in range(len(keys)):
            keys[i] = self._key_listener.canonical(keys[i])
        
        self._hotkeys[shortcut] = pynput.keyboard.HotKey(keys, self._create_hotkey_fun(shortcut))

