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

In other words, just add "# menu title" in the file once, and "# menu
item: &lt;ch&gt;" to create a command from a make file target.  Then
running "makefilemenu Makefile" shows:

    ===== Development tools =====
    a: hello  b: foo

    Choice: 

You can choose one of the commands, and the corresponding target is
made.  To exit, press Control-C or Control-D.  Regular "make" usage is
not interfered, so you can still say "make foo hello" on the command
line to make both targets.

You can also add a few clauses to the Makefile, so that running
makefilemenu is the default target, and your file can be simply
executed:

    #!/usr/bin/env -S make -f
    # -*- makefile -*-

    thisfile := $(lastword $(MAKEFILE_LIST))

    .PHONY: menu
    menu:
        @makefilemenu $(thisfile)
