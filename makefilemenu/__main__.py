"The main entry point of makefilemenu"

import subprocess
import typing

import makefilemenu


def main():
    import calf
    calf.call(makefile_menu)


def makefile_menu(filename: str, *, quit_cmd: str = 'q') -> None:
    """Show a menu from an annotated Makefile

    Args:
        filename: The name of the annotated makefile
        quit_cmd: The command to be used as quit command, empty to skip

    """
    try:
        menu = makefilemenu.Menu.get_menu(filename)
        if quit_cmd:
            menu.add_quit_cmd(quit_cmd)
        while True:
            print('===== %s =====' % menu.title)
            _, columns = (
                int(x) for x in
                subprocess.check_output(['stty', 'size']).decode().split()
            )
            print(menu.to_str(columns))
            item = input('\nChoice: ')
            choice = menu.choices.get(item)
            if choice in menu.quit_cmds:
                break
            if choice:
                ret = subprocess.call(
                    ['make', '-f', filename, '--no-print-directory', choice])
                if ret != 0:
                    print('Error code:', ret)
            elif item:
                print('Command', item, 'not defined')
            print()
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == '__main__':
    main()
