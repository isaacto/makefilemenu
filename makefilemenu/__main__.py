"The main entry point of makefilemenu"

import subprocess
import typing

import makefilemenu


def main():
    import calf
    calf.call(makefile_menu)


def makefile_menu(filename: str) -> None:
    """Show a menu from an annotated Makefile

    Args:
        filename: The name of the annotated makefile

    """
    try:
        menu = makefilemenu.Menu.get_menu(filename)
        while True:
            print('===== %s =====' % menu.title)
            _, columns = (
                int(x) for x in
                subprocess.check_output(['stty', 'size']).decode().split()
            )
            print(menu.to_str(columns))
            item = input('\nChoice: ')
            choice = menu.choices.get(item)
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
