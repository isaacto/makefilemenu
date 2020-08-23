# makefilemenu

Provide a console menu interface for a Makefile.

The canonical use of the system is to have a quick and stupid way to
document commands one would like to run, while at the same time making
it extremely easy to run, without memorizing anything.  Because I'm
(ab)using "make", it is also very easy to run a particular target from
the command line without using the menu system.

Of course nothing stops you from using the tool for a more regular
Makefile.

## Description

This is a very simple system to create a menu from the Makefile.  You
annotate your Makefile as follows:

    # menu title: My title

    # menu item: a
    .PHONY: hello
    hello:
    	echo hello world

    # menu item: b
    .PHONY: foo
    foo:
    	echo foo bar

    # menu comment: Section 2

    # menu item: c
    .PHONY: world
    world:
    	echo 42

In other words, just add "# menu title" in the file once, and "# menu
item: &lt;ch&gt;" to create a command from a make file target.  Then
running "makefilemenu Makefile" shows:

    ===== My title =====
    a: hello  b: foo  q: quit
    Section 2
    c: world

    Choice:

You can choose one of the commands, and the corresponding target is
made.  Note that a "quit" command is automatically added to quit the
program.  If you don't want it, you can use "--quit_cmd ''" to disable
it.  In such case, to exit, press Control-C or Control-D.

Regular "make" usage is not interfered, so you can still say "make foo
hello" on the command line to make both targets.

You can also add a few clauses to the Makefile, so that running
makefilemenu is the default target, and your file can be simply
executed:

    #!/usr/bin/env -S make -f
    # -*- makefile -*-

    thisfile := $(lastword $(MAKEFILE_LIST))

    .PHONY: menu
    menu:
    	@makefilemenu $(thisfile)

## Variables

Two types of variables may be set using `makefilemenu`: environment
variables and Makefile variables.  Environment variables are set using
`# menu envvar`, like this.

    # menu envvar var
    # menu envvar d:var

This adds an initially unset variable `var`, and a menu entry to set
the variable.  In the first case the menu entry is invoked by `var`,
in the second case it is by `d`.

You can set the initial value of the variable to be `val` as follows:

    # menu envvar var=val
    # menu envvar d:var=val

In this case, if an empty value is set on the command line, it is
given an empty value (if there is no default value, an empty value
would unset the variable).

After the environment variable is given a value, when a command is
invoked the make command is invoked with the environment variable set.

You can replace `envvar` by `makevar` in the `# menu` directive above.
In this case, the environment variable is not used, but instead the
`make` command is invoked like:

    make var=val ...
