import os

import pytest

import makefilemenu


def test_basic():
    filename = 'test.mk'
    with open(filename, 'wt') as fout:
        fout.write('''
# menu title: Hello world

# menu item: a
.PHONY: hello
hello:
	echo hello world

# menu item: b
.PHONY: foo
foo:
	echo foo bar
        ''')
    try:
        menu = makefilemenu.Menu.get_menu(filename)
        assert menu.title == 'Hello world'
        assert menu.to_str(15) == 'a: hello\nb: foo'
        assert menu.to_str(20) == '''a: hello  b: foo'''
        menu.add_quit_cmd('q')
        assert menu.to_str(30) == '''a: hello  b: foo  q: quit'''
    finally:
        os.unlink(filename)


def test_error():
    filename = 'test.mk'
    with open(filename, 'wt') as fout:
        fout.write('''
# menu title: Hello world

# menu item: a
.PHONY: hello
hello:
	echo hello world

# menu item: a
.PHONY: foo
foo:
	echo foo bar
        ''')
    try:
        with pytest.raises(AssertionError):
            makefilemenu.Menu.get_menu(filename)
    finally:
        os.unlink(filename)
