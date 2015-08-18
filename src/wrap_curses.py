import os
import curses

# Archipelago, a multi-user dungeon (MUD) server, by Martin Keegan
#
# Copyright (C) 2009-2015  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the GNU Affero General Public Licence as published by
# the Free Software Foundation, either version 3 of said Licence, or
# (at your option) any later version.

def run_alt(cls, main):
    import os

    if "TERM" not in os.environ:
        os.environ["TERM"] = "vt100"
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    try:
        msg = ""
        msg = main(cls, stdscr)
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        os.system("stty sane") # screw you, ncurses
        print "\r" + msg
