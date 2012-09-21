#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Commands handlers modul"""
import random, pickle, sys
from modules.world.map2d import Map_generator_2D
from modules.world.map3d import Generate_Heights
from modules.drive.support import ThreadDo
from modules.drive.world import generate_map_texture, show_terrain, generate_heights_image
from modules.drive.textures import textures
from pandac.PandaModules import Texture

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
            seed = int(params[0])
        else:
            seed = random.randint(0, sys.maxint)

        self.game.world.seed = seed

        def doit():
            global_map_gen = Map_generator_2D(seed = seed)
            complete_i = 0
            for e, (i, desc) in enumerate(global_map_gen.start()):
                self.cmd_write(['{0} * step: {1} / {2}'.format(e, i,desc)])
                if self.game.mode == 'GUI':
                    self.game.write('Generate and show map')
                    world = global_map_gen.maps[complete_i]
                    world.water_z = 0
                    textures['world_map'] = generate_map_texture(world)
                    self.cmd_show_map()
                complete_i = i
            if self.game.mode == 'console':
                self.cmd_write([global_map_gen.maps.show_acii()])
            elif self.game.mode == 'GUI':
                self.cmd_write(['Start generation 3d heights'])
                self.game.world.map_2d = global_map_gen.maps[complete_i]

                gen3d = Generate_Heights(map2d = self.game.world.map_2d,
                                                          seed = seed)
                for e, (i, desc) in enumerate(gen3d.start()):
                    self.game.write('{0} * step: {1} / {2}'.format(e, i,desc))

                self.game.world.map_3d = gen3d.map3d
                self.cmd_write(['Start generation textures of map'])
                textures['world_map'] = generate_map_texture(self.game.world.map_3d)
                self.cmd_show_map()
                #self.cmd_write(['Start generation heights of map'])
                #self.game.world.map_3d.create_height_map('/tmp/heights.png')
                #textures['world_heights'] = generate_heights_image(self.game.world.map_3d)
                self.cmd_hide_map()
                self.cmd_show_terrain()
            self.cmd_write(['Map generation process has been completed. Seed: {0}'.format(\
                                                self.game.world.seed)])

        ThreadDo(doit).start()


        self.cmd_write(['Map generation process has been started'])

    def cmd_show_map(self, params = []):
        """
        docstring for cmd_show_map
        """
        if textures.has_key('world_map'):
            self.game.process.screen_images.add_image('world_map', 
                                        textures['world_map'], 
                                        scale = 0.7)

    def cmd_show_heights(self, params = []):
        """
        """
        if textures.has_key('world_heights'):
            tex = Texture()
            tex.load(textures['world_heights'])
            self.game.process.screen_images.add_image('world_heights', 
                                        tex, scale = 0.7)

    def cmd_hide_heights(self, params = []):
        self.game.process.screen_images.del_image('world_heights')

    def cmd_hide_map(self, params = []):
        """
        docstring for cmd_hide_map
        """
        self.game.process.screen_images.del_image('world_map')

    def cmd_show_terrain(self, params = []):
        """
        """
        show_terrain(self.game.world.map_3d)

    def cmd_save(self, params = []):
        """
        docstring for cmd_save
        """
        pickle.dump(self.game.world.map_2d, open('saves/map_2d.sav', 'w'))

    def cmd_seed(self, params = []):
        """
        """
        self.cmd_write([str(self.game.world.seed)])

    def cmd_load(self, params):
        """
        docstring for cmd_load
        """
        self.game.world.map_2d = pickle.load(open('saves/map_2d.sav', 'r'))
        textures['world_map'] = generate_map_texture(self.game.world.map_2d)
        self.cmd_show_map()

    def cmd_handle(self, raw_cmd):
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
                'showterrain': cmd_show_terrain,
                'showheights': cmd_show_heights,
                'hideheights': cmd_hide_heights,
                'seed': cmd_seed,
              }
# vi: ts=4 sw=4

