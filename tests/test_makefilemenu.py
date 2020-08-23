from unittest.mock import Mock
import os

import pytest

import makefilemenu


def test_basic(mocker):
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

# menu envvar: x
# menu makevar: y=2
        ''')
    try:
        menu = makefilemenu.Menu(filename)
        menu.setup()
        assert menu.to_str(15) == '===== Hello world =====\na: hello\n' \
            'b: foo\nx: Set x\ny: Set y'
        assert menu.to_str(20) == '===== Hello world =====\n'\
            'a: hello  x: Set x\nb: foo    y: Set y'
        menu.add_quit_cmd('q')
        assert menu.to_str(30) \
            == '===== Hello world =====\na: hello  x: Set x  q: quit\n' \
            'b: foo    y: Set y'
        input_func = Mock()
        assert menu.invoke('q', input_func) == ('', True)
        proc_call = mocker.patch('subprocess.call')
        proc_call.return_value = 0
        assert menu.invoke('a', input_func) == ('', False)
        proc_call.assert_called_once_with(
            ['make', '-f', 'test.mk', '--no-print-directory', 'y=2', 'hello'],
            env=mocker.ANY)
        proc_call.reset_mock()
        input_func.return_value = '42'
        assert menu.invoke('y', input_func) == ('', False)
        input_func.assert_called_once_with('y=', '2')
        input_func.return_value = 'foo'
        assert menu.invoke('x', input_func) == ('', False)
        assert menu.invoke('a', input_func) == ('', False)
        proc_call.assert_called_once_with(
            ['make', '-f', 'test.mk', '--no-print-directory', 'y=42', 'hello'],
            env=mocker.ANY)
        proc_call.return_value = 1
        assert menu.invoke('a', input_func) == ('Error code: 1\n', False)
        assert menu.invoke('foo', input_func) == \
            ('Command "foo" not defined\n', False)
    finally:
        os.unlink(filename)


def test_error():
    filename = 'test.mk'
    with open(filename, 'wt') as fout:
        fout.write('''
# menu comment: Hello world

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
        menu = makefilemenu.Menu(filename)
        with pytest.raises(AssertionError):
            menu.setup()
    finally:
        os.unlink(filename)
