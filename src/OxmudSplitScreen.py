
# Archipelago, a multi-user dungeon (MUD) server, by Martin Keegan
#
# Copyright (C) 2009-2012  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the GNU Affero General Public Licence as published by
# the Free Software Foundation, either version 3 of said Licence, or
# (at your option) any later version.

from SplitScreen import SplitScreen

class OxmudSplitScreen(SplitScreen):
    def fixup_line(self, line):
        return line.replace('\0', '0')
    
