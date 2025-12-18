import re
from . import utilities as u
from . import shortcut_binder as sb
from . import globals as g
from typing import Union
import subprocess
import pynput
import threading
import ctypes
import sys

class PynputBinder(sb.KeyBinder):
    # Polling interval in seconds for the key state monitor thread
    KEY_STATE_POLL_INTERVAL = 0.1

    def __init__(self):
        self._hotkeys: dict[str, pynput.keyboard.HotKey] = {}
        self._pressed_keys: set = set()
        self._keys_lock = threading.Lock()
        self._key_listener = pynput.keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._key_listener.start()
        
        self._monitor_stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._key_state_monitor, daemon=True)
        self._monitor_thread.start()
        
        super().__init__()

    def _is_key_physically_pressed(self, key) -> bool:
        """Check if a key is physically pressed using the OS API."""
        try:
            vk = None
            if hasattr(key, 'vk') and key.vk is not None:
                vk = key.vk
            elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
                vk = key.value.vk
            
            if vk is not None:
                # GetAsyncKeyState returns negative if key is pressed
                # Windows
                if hasattr(ctypes, "windll"):
                    return ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 != 0
                # Linux (X11)
                elif hasattr(ctypes, "cdll"):
                    if sys.platform.startswith("linux"):
                        # Try to use Xlib to check key state
                        try:
                            import Xlib.display
                            display = Xlib.display.Display()
                            keycode = display.keysym_to_keycode(vk)
                            state = display.query_keymap()
                            return bool(state[keycode // 8] & (1 << (keycode % 8)))
                        except Exception:
                            pass
        except Exception:
            pass
        return False

    def _key_state_monitor(self):
        """Background thread that checks if pressed keys are still physically held."""
        while not self._monitor_stop_event.wait(self.KEY_STATE_POLL_INTERVAL):
            with self._keys_lock:
                if not self._pressed_keys:
                    continue
                
                keys_to_release = []
                for key in self._pressed_keys:
                    if not self._is_key_physically_pressed(key):
                        keys_to_release.append(key)
                
                for key in keys_to_release:
                    self._pressed_keys.discard(key)
                    for hotkey in self._hotkeys.values():
                        try:
                            hotkey.release(key)
                        except Exception:
                            pass


    def _on_press(self, key):
        can = self._key_listener.canonical(key)
        with self._keys_lock:
            self._pressed_keys.add(can)
            for hotkey in self._hotkeys.values():
                hotkey.press(can)

    def _on_release(self, key):
        can = self._key_listener.canonical(key)
        with self._keys_lock:
            self._pressed_keys.discard(can)
            for hotkey in self._hotkeys.values():
                hotkey.release(can)


    def _deregister_key_binding(self, shortcut: str):
        with self._keys_lock:
            if shortcut in self._hotkeys:
                del self._hotkeys[shortcut]

    def cleanup(self):
        self._monitor_stop_event.set()
        self._monitor_thread.join(timeout=1.0)
        self._key_listener.stop()

    def _create_hotkey_fun(self, shortcut: str):
        def fun():
            self.handle_shortcut(shortcut)
        return fun


    def _register_key_binding(self, shortcut):
        with self._keys_lock:
            if shortcut in self._hotkeys:
                return
            keys = pynput.keyboard.HotKey.parse(shortcut)
            for i in range(len(keys)):
                keys[i] = self._key_listener.canonical(keys[i])
            
            self._hotkeys[shortcut] = pynput.keyboard.HotKey(keys, self._create_hotkey_fun(shortcut))

