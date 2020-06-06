"Get a menu from a Makefile, and convert it to text form for printing"

import collections
import itertools
import math
import re
import typing

import attr


DIRECTIVE_RE = re.compile(r'^#\s*menu\s+(item|title|comment):\s*(.*)\s*$')
TARGET_RE = re.compile(r'^([^#\s].+?)\s?:')


SubmenuType = typing.Dict[str, str]


@attr.s
class Menu:  # pylint: disable=too-few-public-methods
    "Represent the menu"
    entries = attr.ib()  # type: typing.List[typing.Union[str, SubmenuType]]
    quit_cmds = attr.ib() # type: typing.Set[str]

    @classmethod
    def get_menu(cls, filename: str) -> 'Menu':
        """Get the menu by reading menu items marked in the Makefile

        Args:
            filename: The name of the Makefile

        """
        ret = cls([], set())
        pending = None
        with open(filename, 'rt') as fin:
            for line in fin:
                match = DIRECTIVE_RE.match(line)
                if match:
                    if match.group(1) == 'title':
                        ret.entries.append('===== %s =====' % match.group(2))
                    elif match.group(1) == 'comment':
                        ret.entries.append(match.group(2))
                    if match.group(1) == 'item':
                        pending = match.group(2)
                    continue
                if not pending:
                    continue
                match = TARGET_RE.match(line)
                if match:
                    target = match.group(1).split()[0]
                    if target[0] != '.':
                        ret.add_command(pending, target, False)
                        pending = None
        return ret

    def add_command(self, pending: str, target: str, first: bool) -> None:
        assert pending not in self.choices, 'Conflicting command %s' % pending
        submenu = None
        if first:
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
        submenu[pending] = target

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
        self.add_command('q', 'quit', True)
        self.quit_cmds.add('quit')

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
        ret = []  # type: typing.List[str]
        for entry in self.entries:
            if not isinstance(entry, dict):
                ret.append(entry)
            else:
                self._convert_submenu(ret, entry, widths)
        return '\n'.join(ret)

    def _get_widths(self, num_col: int) -> typing.List[int]:
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
    def _convert_submenu(cls, ret: typing.List[str], submenu: SubmenuType,
                         widths: typing.List[int]) -> None:
        item_strs = list(cls._submenu_itemstrs(submenu))
        num_row = math.ceil(len(item_strs) / len(widths))
        splitted = []  # type: typing.List[typing.List[str]]
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
