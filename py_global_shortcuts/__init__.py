import platform
import sys
from . import globals as g
from . import shortcut_binder as sb
from . import utilities as u

_binder: sb.ShortcutBinder = None
_comms = None

def init(appname, cache_dir="./temp"):
    import os

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    g.cache_file = os.path.join(cache_dir, g.CACHE_FILE_NAME)

    if not os.path.exists(g.cache_file):
        with open(g.cache_file, "w") as f:
            f.write("{}")

    g.appname = appname

    global _binder
    if u.is_gnome_wayland():
        global _comms
        from . import linux_comms
        _comms = linux_comms.ProcessCommunicator.get_global_communicator()
        from .gnome_binder import GnomeBinder
        _binder = GnomeBinder()
        _comms.start_server(_binder.handle_shortcut)
    else:
        raise NotImplementedError(f"Shortcut binder not implemented for {platform.system()} yet.")

def deinit():
    global _comms
    if _comms is not None:
        _comms.cleanup()
    if _binder is not None:
        _binder.cleanup()

def binding_handle(appname):
    g.appname = appname
    if len(sys.argv) < 4:
        return
    if g.BINDING_ID_STR == sys.argv[1]:
        pygsstr, input_appname, unique_id = sys.argv[2].split("__")
        shortcut = sys.argv[3]
        assert pygsstr == "pygs"
        print("Handling binding for app:", sys.argv)
        if input_appname != appname:
            # This is not our binding, ignore
            print("App name does not match, exiting.", appname, g.appname)
            exit(0)
        print("Setting unique ID to", unique_id)
        u.set_unique_id(unique_id)
        print("Setting unique ID to", unique_id, u.unique_id())
        if u.is_gnome_wayland():
            from . import linux_comms
            comms = linux_comms.ProcessCommunicator.get_global_communicator()
            if not comms.socket_exists():
                # No socket to communicate with, exit
                print("No socket to communicate with, exiting.")
                exit(0)
            print("Sending shortcut activation for", shortcut)
            comms.send_json({"shortcut": f"{shortcut}"})
        exit(0)

def get_binder() -> sb.ShortcutBinder:
    global _binder
    if _binder is None:
        raise RuntimeError("Binder not initialized. Call init() first.")
    return _binder
