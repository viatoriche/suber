#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)

Grap modul, for render and show all >_<
"""
from config import Config
from direct.gui.DirectGui import DirectButton, DirectEntry
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from modules.drive.camera import CamFree
from modules.drive.support import generate_hash
from modules.drive.textures import textures
from panda3d.core import TextNode, LODNode, NodePath
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import loadPrcFileData
from modules.drive.world import World

loadPrcFileData("", "window-title {0}".format(Config().name_game))
loadPrcFileData("editor-startup", "show-frame-rate-meter #t")

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
    config = Config()
    def __init__(self, game):
        """
        Initialization of GUI Class

        args:
            game - game object
            app - PandaApp
            camFree - camera
            screen_mages - all images
            screem_buttons - all buttons
            entries = text edits
        """

        self.game = game
        self.app = PandaApp()

        self.screen_images = OnscreenImages()
        self.screen_texts = OnscreenTexts()
        self.buttons = DirectButtons()
        self.entries = DirectEntries()

        textures['sight'] = loader.loadTexture('games/{0}/res/textures/sight.png'.format(self.config.game))
        #self.game.world = World(self, self.game)
        #self.app.camera.setPos(0, 0, 200)


    def write(self, text):
        """
            write Text on screen
        """
        self.screen_texts['status'].setText(text)

    def start(self):
        """
        run GUI
        """
        # start plugin game
        self.camFree = CamFree(self.game)
        self.app.camera.setHpr(0, -90, 0)

        self.game.child_game.start()
        self.app.run()

# vi: ft=python:tw=0:ts=4

