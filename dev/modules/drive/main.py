#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Main drive modul"""

import os
import signal
import logging

from modules.drive.commands import Command_Handler
from modules.drive.console import Console_UI
from modules.drive.graph import GUI
from config import Config

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
    prompt = 'Suber> '
    tick = 1
    live = True
    config = Config()

    def __init__(self, mode = 'console', cheat_enable = True):
        Root.__init__(self)


        self.cheat_enable = cheat_enable
        signal.signal(signal.SIGINT, self.signal_stop)
        signal.signal(signal.SIGTERM, self.signal_stop)

        self.log('Game init')

        self.mode = mode
        self.command_handler = Command_Handler(self)
        if self.mode == 'console':
            self.process = Console_UI(self)
        elif self.mode == 'GUI':
            self.process = GUI(self)

    def cmd_handle(self, cmd):
        self.command_handler.cmd_handle(cmd)

    def write(self, text):
        self.process.write(text)

    def start(self):
        self.process.start()

    def log(self, msg):
        logging.info(msg)

    def stop(self):
        self.live = False
        self.process.write('Good bye')
        os._exit(0)

    def signal_stop(self, signum, frame):
        self.stop()


# vi: ts=4 sw=4

