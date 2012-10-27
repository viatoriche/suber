#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main module - run the game

Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
"""

import os
import signal
from pandac.PandaModules import TransparencyAttrib, PointLight, Fog
from modules.textures import TextureCollection
from modules.commands import Command_Handler
from modules.graph import GUI
from modules.interactive import CamManager, MoveAvatar, CollisionAvatar
from direct.actor.Actor import Actor
from voxplanet.world import World
from voxplanet.config import Config as VoxConfig
from voxplanet.params import Params as VoxParams
from panda3d.core import VBase4
from pandac.PandaModules import loadPrcFileData, PStatClient, AmbientLight
from config import Config

loadPrcFileData("", "window-title {0}".format(Config().name_game))
loadPrcFileData("editor-startup", "show-frame-rate-meter #t")
loadPrcFileData("want-pstats", "1")
loadPrcFileData("task-timer-verbose", "1")
loadPrcFileData("pstats-tasks", "1")
loadPrcFileData("", "support-threads #t")
#loadPrcFileData("", "threading-model cull/draw")

PStatClient.connect()

class Main():
    """Main class for game
    """
    def __init__(self):
        self.gui = GUI(self)
        self.cmd_handler = Command_Handler(self)
        self.textures = TextureCollection(self)


        signal.signal(signal.SIGINT, self.signal_stop)
        signal.signal(signal.SIGTERM, self.signal_stop)


    def signal_stop(self, signum, frame):
        self.stop()

    def stop(self):
        self.write('Good bye')
        os._exit(0)

    def write(self, text):
        """Write Text on screen
        """
        self.gui.screen_texts['status'].setText(text)

    def start(self):
        self.textures.load_all()

        self.char = Actor("res/models/ralph",
                                {"run":"res/models/ralph-run",
                                "walk":"res/models/ralph-walk"})
        self.char.pose('walk', 5)
        self.char.setScale(.2)
        self.char.setH(180)

        self.gui.buttons.add_button(name = 'Exit', text = ("Exit", "Exit", "Exit", "disabled"),
                               pos = (1.23, 0, -0.95),
                               scale = 0.07, command=self.stop)

        self.gui.screen_texts.add_text(name = 'status',
                               text = 'Hello! Suber was started!',
                               pos = (-1.3, -0.95), scale = 0.07)
        #self.gui.entries.add_entry(name = 'console',text = "" ,
                               #pos = (-1.29, 0, -0.85),
                               #scale=0.07,command=self.cmd_handler.cmd_handle,
                               #initialText="", width = 37, numLines = 1,focus=0)
        self.gui.screen_texts.add_text(name = 'help',
                               text = 'F5 - create world\nm - toggle map\nF1 - toggle'+\
                               ' help\nEsc - exit\nF10 - render info\n'+\
                               'F2/F3 - 1st/3d person camera\n'+\
                               'F4 - toggle fly/terrain\n'+\
                               'F9 - Cam disable\n'+\
                               'F8 - Toggle Collisions\n'+\
                               'F11/F12 - toggle polygons / disable textures',
                               pos = (-1, 0.8), scale = 0.07)

        self.gui.hotkeys.accept('f1', self.toggle_help)

        self.gui.screen_images.add_image('sight',
                               self.textures['sight'],
                               scale = 0.05, pos = (0, 0, 0))
        self.gui.screen_images['sight'].setTransparency(TransparencyAttrib.MAlpha)


        plight = PointLight('plight')
        sun = self.gui.render.attachNewNode(plight)
        sun.setPos(-32768, 32768, 20000)
        self.gui.render.setLight(sun)

        alight = AmbientLight('alight')
        alight.setColor(VBase4(0.5, 0.5, 0.5, 1))
        alnp = self.gui.render.attachNewNode(alight)
        self.gui.render.setLight(alnp)

        colour = (0.28125, 0.53125, 0.80859375)
        fog = Fog("A linear-mode Fog node")
        fog.setColor(*colour)
        fog.setLinearFallback(0,500,550)
        self.gui.camera.attachNewNode(fog)

        colour = (0.28125, 0.53125, 0.80859375)
        self.gui.render.setFog(fog)
        self.gui.setBackgroundColor(*colour)

        self.cam_manager = CamManager(self)
        self.move_avatar = MoveAvatar(self)

        self.vox_config = VoxConfig()
        self.vox_params = VoxParams()
        self.vox_params.gui = self.gui
        self.vox_params.avatar = self.cam_manager.node
        self.vox_params.status = self.write
        self.vox_params.root_node = self.gui.render
        self.vox_params.chunks_tex = self.textures['world_blocks']
        self.vox_params.tex_uv_height = self.textures.get_block_uv_height
        self.vox_params.tree_tex = self.textures['tree']
        self.vox_params.leafModel = self.gui.loader.loadModel("res/models/shrubbery")
        self.vox_params.leafTex = self.textures['leaf']
        self.vox_params.fog = fog

        self.world = World(self.vox_config, self.vox_params)

        self.collision_avatar = CollisionAvatar(self)

        #self.vox_params.sun = sun

        self.gui.taskMgr.setupTaskChain('Ticker', tickClock = True)
        self.gui.taskMgr.doMethodLater(0.05, self.ticker, 'taskTicker', taskChain = 'Ticker')

        self.gui.start()

    def ticker(self, task):
        return task.again

    def toggle_help(self):
        if self.gui.screen_texts['help'].isHidden():
            self.gui.screen_texts['help'].show()
        else:
            self.gui.screen_texts['help'].hide()

# vi: ft=python:tw=0:ts=4

