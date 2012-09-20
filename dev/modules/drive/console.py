#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Console UI"""

class Console_UI():
    def __init__(self, game):
        # game Object
        self.game = game

    def write(self, text):
        print text

    def start(self):
        self.write('Hello! Suber was started!')
        while self.game.live:
            cmd = raw_input(self.game.prompt)
            self.game.command_handler.handle(cmd)
            if cmd == 'exit':
                break

# vi: ts=4 sw=4

