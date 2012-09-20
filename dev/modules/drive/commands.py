#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Commands handlers modul"""
import random, pickle
from modules.world.map2d import Map_generator_2D
from modules.drive.support import ThreadDo
from modules.drive.world import generate_map_texture
from modules.drive.textures import textures

class Command_Handler():

    def __init__(self, game):
        self.game = game

    def cmd_exit(self, params = []):
        self.game.stop()

    def cmd_write(self, params = []):
        if len(params) > 0:
            text = ' '.join(params)
            self.game.write(text)

    def cmd_create_global_map(self, params = []):
        """
        Generate global map template and show it
        """
        if len(params) >0:
            seed = params[0]
        else:
            seed = random.randint(1,65535)

        def doit():
            global_map_gen = Map_generator_2D(seed = seed)
            complete_i = 0
            for e, (i, desc) in enumerate(global_map_gen.start()):
                self.game.write('{0} * step: {1} / {2}'.format(e, i,desc))
                if self.game.mode == 'GUI':
                    if complete_i < i:
                        self.game.write('Generate and show map')
                        world = global_map_gen.maps[complete_i]
                        textures['world_map'] = generate_map_texture(world)
                        self.cmd_show_map()
                        complete_i = i
            if self.game.mode == 'console':
                self.game.write(global_map_gen.maps.show_acii())
            elif self.game.mode == 'GUI':
                self.game.write('Start generation texture map')
                self.game.world.map_2d = global_map_gen.maps[complete_i]
                textures['world_map'] = generate_map_texture(self.game.world.map_2d)
                self.cmd_show_map()
            self.game.write('Map generation process has been completed')

        ThreadDo(doit).start()

        self.game.write('Map generation process has been started')

    def cmd_show_map(self, params = []):
        """
        docstring for cmd_show_map
        """
        if textures.has_key('world_map'):
            self.game.process.screen_images.add_image('world_map', 
                                        textures['world_map'], 
                                        scale = 0.7)

    def cmd_hide_map(self, params = []):
        """
        docstring for cmd_hide_map
        """
        self.game.process.screen_images.del_image('world_map')

    def cmd_save(self, params = []):
        """
        docstring for cmd_save
        """
        pickle.dump(self.game.world.map_2d, open('saves/map_2d.sav', 'w'))

    def cmd_load(self, params):
        """
        docstring for cmd_load
        """
        self.game.world.map_2d = pickle.load(open('saves/map_2d.sav', 'r'))
        textures['world_map'] = generate_map_texture(self.game.world.map_2d)
        self.cmd_show_map()

    def handle(self, raw_cmd):
        if raw_cmd == '':
            return
        name_cmd = raw_cmd.split()[0]

        try:
            params = raw_cmd.split()[1:]
        except IndexError:
            params = []

        if name_cmd in self.run_cmd:
            self.run_cmd[name_cmd](self, params)

    run_cmd = { 
                'exit': cmd_exit,
                'createmap': cmd_create_global_map,
                'write': cmd_write,
                'showmap': cmd_show_map,
                'hidemap': cmd_hide_map,
                'save': cmd_save,
                'load': cmd_load,
              }
# vi: ts=4 sw=4

