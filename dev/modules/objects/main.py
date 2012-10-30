#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Main classes"""

class RootObject():
    """Root object for all objects of game

    id - uniq ID for object
    game - Main instance
    """
    def __init__(self, game, id):
        self.game = game
        self.id = id

# vi: ts=4 sw=4

