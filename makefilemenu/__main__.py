"The main entry point of makefilemenu"

import fcntl
import readline
import struct
import termios
import typing

import makefilemenu


def main() -> None:
    import calf
    calf.call(makefile_menu)


def rlinput(prompt: str, prefill: str = '') -> str:
    """Input with readline allowing prefill text

    Args:

        prompt: The input prompt
        prefill: The text to prefill

    """
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def makefile_menu(filename: str, *, quit_cmd: str = 'q') -> None:
    """Show a menu from an annotated Makefile

    Args:
        filename: The name of the annotated makefile
        quit_cmd: The command to be used as quit command, empty to skip

    """
    try:
        menu = makefilemenu.Menu(filename)
        menu.setup()
        if quit_cmd:
            menu.add_quit_cmd(quit_cmd)
        while True:
            # Get windows size
            wsz = fcntl.ioctl(0, termios.TIOCGWINSZ, '        ') # type: ignore
            columns = struct.unpack('@4H', wsz)[1]
            print(menu.to_str(columns))
            to_print, to_exit = menu.invoke(input('\nChoice: '), rlinput)
            print(to_print)
            if to_exit:
                return
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == '__main__':
    main()
