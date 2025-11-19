import uuid
import platform
import os
import sys

from . import globals as g

_unique_id_str = str(uuid.uuid4())

def set_unique_id(id_str: str):
    global _unique_id_str
    _unique_id_str = id_str

def app_id():
    return f"pygs__{g.appname}"

def unique_id():
    return f"{app_id()}__{_unique_id_str}"

def is_gnome_wayland():
    if platform.system() != "Linux":
        return False
    return os.environ.get("XDG_SESSION_TYPE") == "wayland" and "ubuntu" in os.environ.get("DESKTOP_SESSION", "")

def get_exec_bash(shortcut: str = ""):
    main_python_file = os.path.abspath(sys.argv[0])

    shortcut = shortcut.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`").replace("<", "\\<").replace(">", "\\>")

    return f"{sys.executable} {main_python_file} {g.BINDING_ID_STR} {unique_id()} {shortcut}"

