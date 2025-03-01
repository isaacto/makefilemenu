"The main entry point of makefilemenu"

import fcntl
import functools
import os
import struct
import termios
import typing

import makefilemenu


def main() -> None:
    import calf
    calf.call(makefile_menu)


try:
    import readline

except ImportError:

    def setup_completer(choices: typing.Optional[typing.List[str]]) -> None:
        "Dummy set completer function"

    def rlinput(prompt: str, prefill: str = '') -> str:
        """Fallback input ignoring prefill text

        Args:

            prompt: The input prompt
            prefill: The text to prefill

        """
        return input(prompt)

else:
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind -e")
        readline.parse_and_bind("bind '\t' rl_complete")
    else:
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(
            readline.get_completer_delims().replace('/', ''))


    basic_completer = readline.set_completer


    if 'pyrepl' in readline.__doc__:  # Home brew a path completer

        def path_completer(text: str, state: int) -> str:
            tdir = readline.get_line_buffer()[:readline.get_begidx()]
            name = [f for f in os.listdir(tdir) if f.startswith(text)][state]
            return f'{name}/' if os.path.isdir(f'{tdir}/{name}') else name

        basic_completer = functools.partial(
            readline.set_completer, path_completer)


    def setup_completer(choices: typing.Optional[typing.List[str]]) -> None:
        "Set completer"
        if not choices:
            basic_completer()
        else:
            def _completer(text: str, state: int) -> str:
                assert choices
                avail = [x for x in choices if x.startswith(text)]
                return avail[state]
            readline.set_completer(_completer)


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
            print(menu.to_str(columns) + '\n')
            setup_completer(sorted(menu.cmds.keys()))
            res = input('Choice: ')
            setup_completer(None)
            try:
                to_print, to_exit = menu.invoke(res, rlinput)
                print(to_print)
                if to_exit:
                    return
            except KeyboardInterrupt:
                pass
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == '__main__':
    main()
