import py_global_shortcuts as pygs
MY_APP_NAME = "my_app"

# Must be the first thing called in the main script
# Yes this looks odd, but it is required!
if __name__ == "__main__":
    pygs.binding_handle(MY_APP_NAME)

import time
import sys

def call_this():
    print("Shortcut activated!")

def main():
    pygs.init(MY_APP_NAME, cache_dir="./temp")
    binder = pygs.get_binder()
    binder.add_binding("<Ctrl><Alt>H", call_this)
    print(binder.get_current_bindings())
    binder.remove_binding("<Ctrl><Alt>H")
    print(binder.get_current_bindings())

if __name__ == "__main__":
    try:
        main()
    finally:
        print("Deinitializing pygs...")
        pygs.deinit()
