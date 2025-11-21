import py_global_shortcuts as pygs
MY_APP_NAME = "my_app"

# Must be the first thing called in the main script
# Yes this looks odd, but it is required!
if __name__ == "__main__":
    pygs.binding_handle(MY_APP_NAME)

import time
import sys

index = 0

def call_this():
    global index
    print("Shortcut activated!", index)
    index += 1

def disabled_call():
    print("This should not be called!")

command1 = pygs.Command("my_command1", call_this)
command2 = pygs.Command("my_command2", call_this)
command3 = pygs.Command("my_command3", disabled_call)

def main():
    pygs.init(MY_APP_NAME, cache_dir="./temp")
    binder = pygs.get_binder()
    binder.register_command(command1)
    binder.register_command(command2)
    binder.register_command(command3)
    binder.link_command("<ctrl>+<alt>+h", command1)
    binder.link_command("<ctrl>+<alt>+h", command3)
    binder.unlink_command("<ctrl>+<alt>+h", command3)
    print(binder.get_key_bindings())
    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Deinitializing pygs...")
        pygs.deinit()

