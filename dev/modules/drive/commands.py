#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Commands handlers modul"""
import random, pickle, sys

from config import Config
from modules.drive.support import ThreadDo
from modules.drive.textures import textures
from modules.drive.world import World
from modules.world.map2d import Map_generator_2D
from modules.world.map3d import Map3d
from pandac.PandaModules import loadPrcFileData

class Command_Handler():
    """Handler for all commands
    """

    config = Config()

    def __init__(self, game):
        self.game = game
        self.minimap = True

    def cmd_exit(self, params = []):
        """Exit the game
        """
        self.game.stop()

    def cmd_write(self, params = []):
        """Write to stdout or GUI
        """
        if len(params) > 0:
            text = ' '.join(params)
            self.game.write(text)

    def testmap(self, params = []):
        """
        Generate global map with test seed
        """
        self.cmd_create_global_map([833650645])

    def cmd_create_global_map(self, params = []):
        """
        Generate global map template and show it
        """
        if len(params) >0:
            seed = int(params[0])
        else:
            seed = random.randint(0, sys.maxint)

        self.game.world.seed = seed
        random.seed(seed)

        def doit():
            global_map_gen = Map_generator_2D()
            complete_i = 0
            for e, (i, desc) in enumerate(global_map_gen.start()):
                self.cmd_write(['{0} * step: {1} / {2}'.format(e, i,desc)])
                if self.game.mode == 'GUI':
                    self.game.write('Generate and show map')
                complete_i = i
            if self.game.mode == 'console':
                self.cmd_write([global_map_gen.maps.show_acii()])
            elif self.game.mode == 'GUI':
                self.cmd_write(['Start convertation 2d -> 3d'])
                self.game.world.map_2d = global_map_gen.end_map
                #map3d = Map3d()
                #map3d.get_from_2d(self.game.world.map_2d, seed)
                #self.game.world.map_3d = map3d
                self.game.world.new()
            self.cmd_write(['Map generation process has been completed. Seed: {0}'.format(\
                                                self.game.world.seed)])

        #ThreadDo(doit).start()
        doit()


        self.cmd_write(['Map generation process has been started'])
        loadPrcFileData("", "window-title Suber")



    def cmd_minimap(self, params = []):
        """
        """
        self.minimap = not self.minimap
        if self.minimap:
            self.cmd_show_map()
        else:
            self.cmd_hide_map()

    def cmd_show_map(self, params = []):
        """
        docstring for cmd_show_map
        """
        if self.minimap:
            #textures['world_map'] = generate_map_texture(self.game.world.map_tree, 1)
            self.game.process.screen_images.add_image('world_map', 
                                            textures['world_map'], 
                                            scale = 0.2, pos = (-1.12, 0, 0.79))
            #self.game.process.screen_images['world_map'].show()

    def cmd_hide_map(self, params = []):
        """
        docstring for cmd_hide_map
        """
        self.game.process.screen_images.del_image('world_map')

    def cmd_save(self, params = []):
        """
        docstring for cmd_save
        """
        pickle.dump(self.game.world, open('world.sav', 'w'))

    def cmd_seed(self, params = []):
        """
        """
        self.cmd_write([str(self.game.world.seed)])

    def cmd_load(self, params):
        """
        docstring for cmd_load
        """
        self.game.world = pickle.load(open('world.sav', 'r'))
        random.seed(self.game.world.seed)
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
                'test': testmap,
                'write': cmd_write,
                'showmap': cmd_show_map,
                'hidemap': cmd_hide_map,
                'save': cmd_save,
                'load': cmd_load,
                'minimap': cmd_minimap,
                'seed': cmd_seed,
              }
# vi: ts=4 sw=4

