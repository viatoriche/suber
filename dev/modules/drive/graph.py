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
from modules.drive.world import show_terrain
from panda3d.core import TextNode, LODNode, NodePath
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import loadPrcFileData

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
        """
        self.game = game
        self.app = PandaApp()
        self.app.disableMouse()
        self.camFree = CamFree(showterrain = self.show_terrain)
        self.app.camera.setHpr(0, -90, 0)
        self.default_cam(self.config.root_level)
        self.screen_images = OnscreenImages()
        self.screen_texts = OnscreenTexts()
        self.buttons = DirectButtons()
        self.entries = DirectEntries()
        self.lod = LODNode('suber')
        self.lod_node = NodePath(self.lod)
        self.lod_node.reparentTo(render)
        #render.setShaderInput('time', 0)
        self.buttons.add_button(name = 'Exit', text = ("Exit", "Exit", "Exit", "disabled"),
                                    pos = (1.23, 0, -0.95),
                                    scale = 0.07, command=self.game.stop)

        self.buttons.add_button(name = 'Down', text = ("Down", "Down", "Down", "disabled"),
                                    pos = (1.23, 0, 0.7),
                                    scale = 0.07, command = self.down)
        self.buttons.add_button(name = 'Up', text = ("Up", "Up", "Up", "disabled"),
                                    pos = (1.23, 0, 0.8),
                                    scale = 0.07, command = self.up)

        self.screen_texts.add_text(name = 'status',
                                        text = 'Hello! Suber was started!',
                                        pos = (-1.3, -0.95), scale = 0.07)
        self.entries.add_entry(name = 'console',text = "" , 
                               pos = (-1.29, 0, -0.85), 
                               scale=0.07,command=self.game.cmd_handle,
            initialText="", width = 37, numLines = 1,focus=0)

        textures['sight'] = loader.loadTexture('res/textures/sight.png')
        self.screen_images.add_image('sight', 
                                            textures['sight'], 
                                            scale = 0.05, pos = (0, 0, 0))
        self.screen_images['sight'].setTransparency(TransparencyAttrib.MAlpha)


    def default_cam(self, level):
        self.camFree.level = level


    def down(self):
        level = self.game.world.level
        if level>=self.config.land_level:
            return
        level += 1
        self.camFree.level = level
        self.show_terrain(level)

    def up(self):
        level = self.game.world.level
        if level<=self.config.root_level:
            return
        level -= 1
        self.camFree.level = level
        self.show_terrain(level)

    def show_terrain(self, level):
        show_terrain(self.game, base.camera.getPos(), level)

    def write(self, text):
        """
            write Text on screen
        """
        self.screen_texts['status'].setText(text)

    def start(self):
        """
        run GUI
        """
        self.game.cmd_handle('createmap')
        self.app.run()

# vi: ft=python:tw=0:ts=4

