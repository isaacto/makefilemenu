"Get a menu from a Makefile, and convert it to text form for printing"

import collections
import functools
import itertools
import math
import os
import re
import subprocess
import typing

import attr


__version__ = '0.4.5'


DIRECTIVE_RE = re.compile(
    r'^#\s*menu\s+(item|title|comment|envvar|makevar):\s*(.*)\s*$')
TARGET_RE = re.compile(r'^([^#\s].+?)\s?:')


SubmenuType = dict[str, str]
InputFunc = typing.Callable[[str, str], str]
CmdType = typing.Callable[[InputFunc], tuple[str, bool]]


@attr.s
class Menu:  # pylint: disable=too-few-public-methods
    "Represent the menu"
    filename: str = attr.ib()
    entries: list[typing.Union[str, SubmenuType]] = attr.ib(factory=lambda: [])
    cmds: dict[str, CmdType] = attr.ib(factory=lambda: {})
    em_vars: dict[str, str] = attr.ib(factory=lambda: {})
    em_unsettable: set[str] = attr.ib(factory=lambda: set())

    def setup(self) -> None:
        "Get the menu by reading menu items marked in the Makefile"
        pending = None
        with open(self.filename, 'rt') as fin:
            for line in fin:
                match = DIRECTIVE_RE.match(line)
                if match:
                    if match.group(1) == 'title':
                        self.entries.append('===== %s =====' % match.group(2))
                    elif match.group(1) == 'comment':
                        self.entries.append(match.group(2))
                    elif match.group(1) in ('envvar', 'makevar'):
                        self._addvar(match.group(1), match.group(2))
                    if match.group(1) == 'item':
                        pending = match.group(2)
                    continue
                if not pending:
                    continue
                match = TARGET_RE.match(line)
                if match:
                    target = match.group(1).split()[0]
                    if target[0] != '.':
                        self.add_command(
                            pending, target,
                            functools.partial(self._make, target), False)
                        pending = None

    def _addvar(self, vtype: str, vspec: str) -> None:
        emvar, sep, init = vspec.partition('=')
        name, _, emvar = emvar.partition(':')
        if not emvar:
            emvar = name
        assert name and emvar
        emvar = vtype[0] + emvar
        if sep:
            self.em_vars[emvar] = init
        self.add_command(
            name, 'Set ' + name,
            functools.partial(self._setvar, emvar), False)

    def add_command(self, choice: str, desc: str, cmd: CmdType,
                    to_first: bool) -> None:
        assert choice not in self.choices, 'Conflicting command %s' % choice
        submenu = None
        if to_first:
            for entry in self.entries:
                if isinstance(entry, dict):
                    submenu = entry
                    break
        else:
            if self.entries and isinstance(self.entries[-1], dict):
                submenu = self.entries[-1]
        if submenu is None:
            submenu = collections.OrderedDict()
            self.entries.append(submenu)
        submenu[choice] = desc
        self.cmds[choice] = cmd

    @property
    def choices(self) -> SubmenuType:
        ret = collections.OrderedDict()
        for entry in self.entries:
            if isinstance(entry, dict):
                ret.update(entry)
        return ret

    def add_quit_cmd(self, cmd: str) -> None:
        """Add a quit command

        Args:
            cmd: The command to use

        """
        self.add_command('q', 'quit', self._quit, True)

    def _quit(self, input_func: InputFunc) -> tuple[str, bool]:
        _ = input_func
        return '', True

    def _setvar(self, emvar: str, input_func: InputFunc) -> tuple[str, bool]:
        self.em_vars[emvar] = input_func('%s=' % emvar[1:],
                                         self.em_vars.get(emvar, ''))
        return '', False

    def _make(self, target: str, input_func: InputFunc) -> tuple[str, bool]:
        _ = input_func
        env = os.environ.copy()
        extra = []
        for emvar, val in self.em_vars.items():
            if emvar[0] == 'm':
                extra.append(emvar[1:] + '=' + val)
            else:
                env[emvar[1:]] = val
        ret = subprocess.call(
            ['make', '-f', self.filename, '--no-print-directory',
             *extra, target], env=env)
        if ret != 0:
            return 'Error code: %s\n' % ret, False
        return '', False

    def invoke(self, choice: str, input_func: InputFunc) -> tuple[str, bool]:
        """Invoke a choice

        Args:

            choice: The choice of the user

        Returns:

            A string to print, and an indication about whether the
               command should be interrupted

        """
        if choice in self.cmds:
            return self.cmds[choice](input_func)
        return 'Command "%s" not defined\n' % choice, False

    def to_str(self, columns: int) -> str:
        """Turn the menu to a string

        Args:
            cmd: Maximum length of a line

        """
        widths = [int(1e6)]
        for num_col in range(2, 10):
            new_widths = self._get_widths(num_col)
            if sum(new_widths) + 2 * (len(new_widths) - 1) < columns:
                widths = new_widths
            else:
                break
        ret: list[str] = []
        for entry in self.entries:
            if not isinstance(entry, dict):
                ret.append(entry)
            else:
                self._convert_submenu(ret, entry, widths)
        return '\n'.join(ret)

    def _get_widths(self, num_col: int) -> list[int]:
        ret = [0] * num_col
        for submenu in self.entries:
            if not isinstance(submenu, dict):
                continue
            item_strs = list(self._submenu_itemstrs(submenu))
            num_row = math.ceil(len(item_strs) / num_col)
            for idx, start in enumerate(range(0, len(item_strs), num_row)):
                for item_str in item_strs[start : start + num_row]:
                    ret[idx] = max(ret[idx], len(item_str))
        return ret

    @classmethod
    def _convert_submenu(cls, ret: list[str], submenu: SubmenuType,
                         widths: list[int]) -> None:
        item_strs = list(cls._submenu_itemstrs(submenu))
        num_row = math.ceil(len(item_strs) / len(widths))
        splitted: list[list[str]] = []
        for idx, start in enumerate(range(0, len(item_strs), num_row)):
            splitted.append(list(item_strs[start : start + num_row]))
        for row in itertools.zip_longest(*splitted):
            items = []
            for item, width in zip(row, widths):
                if item:
                    items.append(('%%-%ds' % width) % item)
            ret.append('  '.join(items).rstrip())

    @staticmethod
    def _submenu_itemstrs(submenu: SubmenuType) -> typing.Iterator[str]:
        for key, desc in submenu.items():
            yield '%s: %s' % (key, desc)
