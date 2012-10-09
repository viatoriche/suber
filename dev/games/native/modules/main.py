#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module - run the game
"""

from pandac.PandaModules import TransparencyAttrib
from modules.drive.textures import textures
from games.native.modules.commands import Command_Handler

class Main():
    def __init__(self, game):
        self.game = game
        self.world = game.world
        self.gui = self.game.process
        self.cmd_handler = Command_Handler(self)

    def stop(self):
        self.game.stop()

    def write(self, text):
        """
            write Text on screen
        """
        self.gui.screen_texts['status'].setText(text)

    def start(self):
        self.gui.buttons.add_button(name = 'Exit', text = ("Exit", "Exit", "Exit", "disabled"),
                               pos = (1.23, 0, -0.95),
                               scale = 0.07, command=self.game.stop)

        self.gui.screen_texts.add_text(name = 'status',
                               text = 'Hello! Suber was started!',
                               pos = (-1.3, -0.95), scale = 0.07)
        self.gui.entries.add_entry(name = 'console',text = "" , 
                               pos = (-1.29, 0, -0.85), 
                               scale=0.07,command=self.cmd_handler.cmd_handle,
                               initialText="", width = 37, numLines = 1,focus=0)

        self.gui.screen_images.add_image('sight', 
                               textures['sight'], 
                               scale = 0.05, pos = (0, 0, 0))
        self.gui.screen_images['sight'].setTransparency(TransparencyAttrib.MAlpha)

# vi: ft=python:tw=0:ts=4

