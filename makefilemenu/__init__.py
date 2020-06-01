"Get a menu from a Makefile, and convert it to text form for printing"

import collections
import itertools
import math
import re
import typing

import attr


DIRECTIVE_RE = re.compile(r'^#\s*menu\s+(item|title):\s*(.*)\s*$')
TARGET_RE = re.compile(r'^([^#\s].+?)\s?:')


@attr.s
class Menu:  # pylint: disable=too-few-public-methods
    "Represent the menu"
    title = attr.ib()   # type: str
    choices = attr.ib() # type: typing.Dict[str, str]
    quit_cmds = attr.ib() # type: typing.Set[str]

    @classmethod
    def get_menu(cls, filename: str) -> 'Menu':
        """Get the menu by reading menu items marked in the Makefile

        Args:
            filename: The name of the Makefile

        """
        ret = cls('', collections.OrderedDict(), set())
        pending = None
        with open(filename, 'rt') as fin:
            for line in fin:
                match = DIRECTIVE_RE.match(line)
                if match:
                    if match.group(1) == 'title':
                        ret.title = match.group(2)
                    if match.group(1) == 'item':
                        pending = match.group(2)
                    continue
                if not pending:
                    continue
                match = TARGET_RE.match(line)
                if match:
                    target = match.group(1).split()[0]
                    if target[0] != '.':
                        assert pending not in ret.choices, \
                            'Conflicting command %s' % pending
                        ret.choices[pending] = target
                        pending = None
        return ret

    def add_quit_cmd(self, cmd: str) -> None:
        """Add a quit command

        Args:
            cmd: The command to use

        """
        assert cmd not in self.choices, 'Conflicting cammand %s' % cmd
        self.choices['q'] = 'quit'
        self.quit_cmds.add('quit')

    def to_str(self, columns: int) -> str:
        """Turn the menu to a string

        Args:
            cmd: Maximum length of a line

        """
        splitted = [self.choices]
        try:
            for num_col in range(1, 10):
                splitted = self._get_splitted(self.choices, num_col, columns)
        except RuntimeError:
            pass
        items = [[self._item_str(*i) for i in s.items()] for s in splitted]
        lens = [max(len(x) for x in i) for i in items]
        items = [[('%%-%ds' % lens[col]) % i for i in s]
                 for col, s in enumerate(items)]
        ret = []  # type: typing.List[str]
        for row in itertools.zip_longest(*items):
            ret.append('  '.join(r for r in row if r).rstrip())
        return '\n'.join(ret)

    @classmethod
    def _get_splitted(cls, choices: typing.Dict[str, str], num_col: int,
                      max_len: int) -> typing.List[typing.Dict[str, str]]:
        "Get the result splitting the list of choices into num_col"
        if num_col > len(choices):
            raise RuntimeError('Too short list')
        num_row = math.ceil(len(choices) / num_col)
        ret = []  # type: typing.List[typing.Dict[str, str]]
        items = list(choices.items())
        for start in range(0, len(items), num_row):
            ret.append(collections.OrderedDict(items[start : start + num_row]))
        if 2 * num_col - 2 + sum(cls._get_width(s) for s in ret) > max_len - 1:
            raise RuntimeError('Result too wide')
        return ret

    @classmethod
    def _get_width(cls, choices: typing.Dict[str, str]) -> int:
        "Get the width required for a list of choices if shown in one column"
        return max([0] + list(len(cls._item_str(*item))
                              for item in choices.items()))

    @staticmethod
    def _item_str(key: str, val: str) -> str:
        "The string for a menu item"
        return '%s: %s' % (key, val)
