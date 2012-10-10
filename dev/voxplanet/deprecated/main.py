#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Main drive modul"""

import os
import signal
from modules.drive.commands import Command_Handler
from modules.drive.graph import GUI
from modules.drive.world import World
from config import Config

exec('from games.{0}.modules.main import Main as ChildMain'.format(Config().game))

class Root():
    """
    docstring for Root
    """
    # TODO: do with it anithing 
    def __init__(self):
        """
        docstring for __init__
        """
        pass

class Game(Root):
    """Main class

    """
    live = True
    config = Config()

    def __init__(self, cheat_enable = True):
        Root.__init__(self)

        self.cheat_enable = cheat_enable
        signal.signal(signal.SIGINT, self.signal_stop)
        signal.signal(signal.SIGTERM, self.signal_stop)

        self.process = GUI(self)
        self.world = World(self.process, self)
        self.child_game = ChildMain(self)

    def write(self, info):
        self.child_game.write(info)

    def start(self):
        self.process.start()

    def stop(self):
        self.live = False
        self.process.write('Good bye')
        os._exit(0)

    def signal_stop(self, signum, frame):
        self.stop()


# vi: ts=4 sw=4

