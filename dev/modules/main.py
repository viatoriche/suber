#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module - run the game
"""
import os
import signal
from pandac.PandaModules import TransparencyAttrib
from modules.textures import TextureCollection
from modules.commands import Command_Handler
from modules.graph import GUI
from voxplanet.world import World
from voxplanet.config import Config as VoxConfig
from voxplanet.params import Params as VoxParams

class Main():
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
        """
            write Text on screen
        """
        self.gui.screen_texts['status'].setText(text)

    def start(self):
        self.textures.load_all()
        self.gui.buttons.add_button(name = 'Exit', text = ("Exit", "Exit", "Exit", "disabled"),
                               pos = (1.23, 0, -0.95),
                               scale = 0.07, command=self.stop)

        self.gui.screen_texts.add_text(name = 'status',
                               text = 'Hello! Suber was started!',
                               pos = (-1.3, -0.95), scale = 0.07)
        self.gui.entries.add_entry(name = 'console',text = "" , 
                               pos = (-1.29, 0, -0.85), 
                               scale=0.07,command=self.cmd_handler.cmd_handle,
                               initialText="", width = 37, numLines = 1,focus=0)

        self.gui.screen_images.add_image('sight', 
                               self.textures['sight'], 
                               scale = 0.05, pos = (0, 0, 0))
        self.gui.screen_images['sight'].setTransparency(TransparencyAttrib.MAlpha)

        self.vox_config = VoxConfig()
        self.vox_params = VoxParams()
        self.vox_params.status = self.write
        self.vox_params.root_node = self.gui.render
        self.vox_params.chunks_tex = self.textures['world_blocks']
        self.vox_params.tex_uv_height = self.textures.get_block_uv_height
        self.world = World(self.vox_config, self.vox_params)

        self.gui.start()

# vi: ft=python:tw=0:ts=4
