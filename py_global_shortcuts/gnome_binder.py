import re
from . import utilities as u
from . import shortcut_binder as sb
from . import globals as g
import subprocess


class GnomeBinder(sb.ShortcutBinder):
    def _get_binding_path_prefix(self) -> str:
        return f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/{u.unique_id()}"

    def remove_binding(self, shortcut: str):
        print("Removing binding for shortcut:", shortcut)
        current_bindings = self._get_gsettings_bindings_list()
        bindingpath = f"{self._get_binding_path_prefix()}/{shortcut}/"
        if bindingpath not in current_bindings:
            print("Binding path not found, nothing to remove.")
            return
        current_bindings.remove(bindingpath)
        self._set_gsettings_bindings_list(current_bindings)
        print(current_bindings)
        self._deregister_shortcut(shortcut)


    def _set_gsettings_bindings_list(self, bindings: list[str]):
        subprocess.run(
            ["gsettings", "set", g.GSETTINGS_SCHEMA, g.GSETTINGS_KEY, str(bindings)],
            capture_output=True
        )

    def _remove_current_bindings_from_gsettings(self):
        schema = "org.gnome.settings-daemon.plugins.media-keys"
        key = "custom-keybindings"

        current_bindings = self._get_gsettings_bindings_list()
        updated_bindings = []
        for b in current_bindings:
            if not b.startswith(self._get_binding_path_prefix()):
                updated_bindings.append(b)
        self._set_gsettings_bindings_list(updated_bindings)


    def _get_gsettings_bindings_list(self) -> list[str]:
        # Get the current list of custom keybindings
        result = subprocess.run(
            ["gsettings", "get", g.GSETTINGS_SCHEMA, g.GSETTINGS_KEY],
            capture_output=True,
            text=True
        )

        current_bindings = result.stdout.strip()
        current_bindings = re.sub(r'^@as\s+', '', current_bindings)
        current_bindings = eval(current_bindings)

        return current_bindings

    def _get_current_gsettings_bindings(self):
        current_bindings = self._get_gsettings_bindings_list()

        app_bindings = []
        for binding_path in current_bindings:
            if binding_path.startswith(self._get_binding_path_prefix()):
                # Get the shortcut details for this binding
                binding_schema = f"{g.GSETTINGS_SCHEMA}.custom-keybinding:{binding_path}"
                name = subprocess.run(
                    ["gsettings", "get", binding_schema, "name"],
                    capture_output=True,
                    text=True
                ).stdout.strip().strip("'")
                command = subprocess.run(
                    ["gsettings", "get", binding_schema, "command"],
                    capture_output=True,
                    text=True
                ).stdout.strip().strip("'")
                shortcut = subprocess.run(
                    ["gsettings", "get", binding_schema, "binding"],
                    capture_output=True,
                    text=True
                ).stdout.strip().strip("'")

                app_bindings.append(shortcut)

        return app_bindings

    def cleanup(self):
        self._remove_current_bindings_from_gsettings()

    def add_binding(self, shortcut, function):
        binding_command = f"{u.get_exec_bash(shortcut)}"
        self._register_shortcut(shortcut, function)
        self._add_binding(shortcut, binding_command)

    def _add_binding(self, shortcut, command):
        # Get the current list of custom keybindings
        result = subprocess.run(
            ["gsettings", "get", g.GSETTINGS_SCHEMA, g.GSETTINGS_KEY],
            capture_output=True,
            text=True
        )

        current_bindings = result.stdout.strip()
        current_bindings = re.sub(r'^@as\s+', '', current_bindings)
        current_bindings = eval(current_bindings)

        # Define the new binding path
        new_binding_path = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/{u.unique_id()}/{shortcut.replace(' ', '_')}/"

        # Add the new binding if it doesn't exist
        if new_binding_path not in current_bindings:
            current_bindings.append(new_binding_path)
            subprocess.run(
                ["gsettings", "set", g.GSETTINGS_SCHEMA, g.GSETTINGS_KEY, str(current_bindings)],
                capture_output=True
            )

            # Set the name, command, and binding for the new shortcut
            subprocess.run(
                ["gsettings", "set", f"{g.GSETTINGS_SCHEMA}.custom-keybinding:{new_binding_path}", "name", f"Custom Shortcut {shortcut}"],
                capture_output=True
            )
            subprocess.run(
                ["gsettings", "set", f"{g.GSETTINGS_SCHEMA}.custom-keybinding:{new_binding_path}", "command", command],
                capture_output=True
            )
            subprocess.run(
                ["gsettings", "set", f"{g.GSETTINGS_SCHEMA}.custom-keybinding:{new_binding_path}", "binding", shortcut],
                capture_output=True
            )
