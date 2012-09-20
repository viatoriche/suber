#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)

Grap modul, for render and show all >_<
"""
import hashlib, random
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, GeomPrimitive
from modules.drive.support import generate_hash

class OnscreenImages(dict):
    """
    All screen images collection
    """
    def add_image(self, name = '', filename = '', pos = (0,0,0), scale = 1):
        if name == '':
            name = filename
        if self.has_key(name):
            self.del_image(name)
        self[name] = OnscreenImage(image = filename, pos = pos, scale = scale)
        return self[name]

    def del_image(self, name):
        if self.has_key(name):
            self[name].destroy()
            del self[name]

class OnscreenTexts(dict):
    """
    All screen text collection
    """
    def add_text(self, name = '', text = '', pos = (0,0,0), scale = 1, align = TextNode.ALeft):
        """
        docstring for add_text
        """
        if name == '':
            name = generate_hash(self)
        self[name] = OnscreenText(text = text, align = align, pos = pos, scale = scale)
        return self[name]

    def del_text(self, name):
        """
        docstring for hide_text
        """
        if self.has_key(name):
            self[name].destroy()
            del self[name]

class DirectButtons(dict):
    """
    docstring for DirectButtons
    """
    def add_button(self, name = '', text = ("Button", "Button", "Button", "disabled"),
                                pos = (0,0,0), scale = 1, command = None):
        """
        TODO: add docstring
        """
        if name == '':
            name = generate_hash(self)
        self[name] = DirectButton(text = text, pos = pos, scale = scale,
                                                    command=command)
        return self[name]

class DirectEntries(dict):
    """
    docstring for DirectEntries
    """
    def add_entry(self, name='', text = "" , pos = (0, 0, 0), scale=1, command = None,
            initialText="", width = 15, numLines = 1, focus=1):
        """
        docstring for add_entry
        """
        if name == '':
            name = generate_hash(self)
        self[name] = DirectEntry(text = text, pos = pos, scale = scale,
                                command = command, initialText = initialText,
                                width = width, numLines = numLines, focus = focus)

        return self[name]

class PandaApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

class GUI():
    """
    GUI --- panda3d
    """
    def __init__(self, game):
        """
        Initialization of GUI Class

        args:
            game - game object
        """
        self.game = game
        self.app = PandaApp()
        self.screen_images = OnscreenImages()
        self.screen_texts = OnscreenTexts()
        self.buttons = DirectButtons()
        self.entries = DirectEntries()
        self.buttons.add_button(name = 'Exit', text = ("Exit", "Exit", "Exit", "disabled"),
                                    pos = (1.23, 0, -0.95),
                                    scale = 0.07, command=self.game.stop)
        self.screen_texts.add_text(name = 'status',
                                        text = 'Hello! Suber was started!',
                                        pos = (-1.3, -0.95), scale = 0.07)
        self.entries.add_entry(name = 'console',text = "" , pos = (-1.29, 0, -0.85), scale=0.07,command=self.game.handle,
            initialText="", width = 37, numLines = 1,focus=1)


    def write(self, text):
        """
            write Text on screen
        """
        self.screen_texts['status'].setText(text)

    def start(self):
        """
        run GUI
        """
        self.app.run()

# vi: ft=python:tw=0:ts=4

