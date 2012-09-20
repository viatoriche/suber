#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Initialization"""

from modules.drive.main import Game

def go():
    #game = Game(mode = 'console')
    game = Game(mode = 'GUI')
    game.start()

# vi: ts=4 sw=4

