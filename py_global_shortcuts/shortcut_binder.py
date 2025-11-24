from typing import Callable, Union
from . import globals as g
from . filed_dict import FiledDict, CustomJSONEncoder
import os


class Command:
    def __init__(self, cmd_id: str, function: Callable, name: str = ""):
        self.name = name
        self.function: Callable = function
        self.cmd_id = cmd_id
        if name == "":
            self.name = self.cmd_id


    def __repr__(self):
        return f"Command({self.name}, {self.function})"


    def __str__(self):
        return self.__repr__()


    def execute(self):
        self.function()


class KeyBinding:
    def __init__(self, shortcut: str):
        self.shortcut = shortcut
        self.commands: list[str] = []


    def __repr__(self):
        return f"KeyBinding({self.shortcut}, {self.commands})"


    def __str__(self):
        return self.__repr__()


    def get_commands(self) -> list[str]:
        return self.commands


    def add_command(self, command: Union[Command, str]):
        if isinstance(command, Command):
            command = command.cmd_id
        if self.has_command(command):
            return
        self.commands.append(command)


    def remove_command(self, command: Union[Command, str]):
        if isinstance(command, Command):
            command = command.cmd_id
        if command in self.commands:
            self.commands.remove(command)


    def has_command(self, command: Union[Command, str]) -> bool:
        if isinstance(command, Command):
            command = command.cmd_id
        return command in self.commands


class KeyBinder:
    def __init__(self):
        self.shortcuts: FiledDict[str, KeyBinding] = FiledDict(g.cache_file, autosave=True, default={})
        self.commands: dict[str, Command] = {}
        for shortcut in self.shortcuts.keys():
            self._register_key_binding(shortcut)


    def register_command(self, command: Command):
        self.commands[command.cmd_id] = command


    def get_key_bindings(self) -> list[KeyBinding]:
        return list(self.shortcuts.values())


    def get_key_binding(self, shortcut: str) -> KeyBinding:
        shortcut = self._sanitize_binding_str(shortcut)
        if shortcut in self.shortcuts:
            return self.shortcuts[shortcut]
        return None


    def get_commands(self) -> list[Command]:
        return list(self.commands.values())


    def cleanup(self):
        pass


    def execute_command(self, command_id: Union[Command, str]):
        if isinstance(command_id, Command):
            command_id = command_id.id
        if command_id in self.commands:
            command = self.commands[command_id]
            command.execute()


    def delete_key_binding(self, shortcut: str):
        shortcut = self._sanitize_binding_str(shortcut)
        if shortcut in self.shortcuts:
            del self.shortcuts[shortcut]
            self._deregister_key_binding(shortcut)
        self.shortcuts.save()


    def create_key_binding(self, shortcut: str):
        shortcut = self._sanitize_binding_str(shortcut)
        if shortcut not in self.shortcuts:
            self.shortcuts[shortcut] = KeyBinding(shortcut)
            self._register_key_binding(shortcut)
            self.shortcuts.save()


    def unlink_command(self, shortcut: str, command: Union[Command, str]):
        shortcut = self._sanitize_binding_str(shortcut)
        if isinstance(command, Command):
            command = command.cmd_id
        if shortcut in self.shortcuts:
            self.shortcuts[shortcut].remove_command(command)
        self.shortcuts.save()


    def link_command(self, shortcut: str, command: Union[Command, str]):
        shortcut = self._sanitize_binding_str(shortcut)
        if shortcut not in self.shortcuts:
            self.shortcuts[shortcut] = KeyBinding(shortcut)
        self.shortcuts[shortcut].add_command(command)
        self._register_key_binding(shortcut)
        self.shortcuts.save()


    def handle_shortcut(self, shortcut: str):
        shortcut = self._sanitize_binding_str(shortcut)
        if shortcut in self.shortcuts:
            for command_id in self.shortcuts[shortcut].get_commands():
                if command_id in self.commands:
                    command = self.commands[command_id]
                    command.execute()


    def _register_key_binding(self, shortcut: str):
        raise NotImplementedError("This method should be implemented by subclasses.")


    def _deregister_key_binding(self, shortcut: str):
        raise NotImplementedError("This method should be implemented by subclasses.")


    def _sanitize_binding_str(self, binding_str: str) -> str:
        return binding_str.lower()


def _binding_serializer(bnd: 'KeyBinding'):
    return {
        "shortcut": bnd.shortcut,
        "commands": bnd.get_commands(),
        "_cls_": "KeyBinding"
    }


def _binding_deserializer(dct):
    if "_cls_" in dct and dct["_cls_"] == "KeyBinding":
        ret = KeyBinding(dct["shortcut"])
        for cmd_id in dct["commands"]:
            ret.add_command(cmd_id)
        return ret
    return dct


FiledDict.register_serializer(KeyBinding, _binding_serializer)
FiledDict._custom_dict_deserializer = _binding_deserializer
