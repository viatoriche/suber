#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Commands handlers modul"""
import random, pickle, sys

from config import Config

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

        #seed = 34568

        #seed = 2789334

        print 'Seed of world: ', seed
        self.game.world.seed = seed
        self.game.world.new()




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
            self.game.gui.screen_images.add_image('world_map', 
                                            self.game.world.get_map3d_tex(256), 
                                            scale = 0.8, pos = (0, 0, 0.1))
            #self.game.gui.screen_images['world_map'].show()

    def cmd_hide_map(self, params = []):
        """
        docstring for cmd_hide_map
        """
        self.game.gui.screen_images.del_image('world_map')

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

    def cmd_info(self, params = []):
        """render.analyze()

        """
        print '\n'
        print 'All info stat: '
        print render.analyze()
        for chct in self.game.world.chunks_map.chunks_clts.values():
            hm = sm = dm = am = 0
            for ch_m in chct.chunks_models:
                if chct.chunks_models[ch_m].isHidden():
                    hm += 1
                else:
                    sm += 1
                if chct.chunks_models[ch_m].hasParent():
                    am += 1
                else:
                    dm += 1
            cht = chf = 0
            for ch in chct.chunks:
                if chct.chunks[ch]:
                    cht += 1
                else:
                    chf += 1

            print 'Chunks models:', len(chct.chunks_models),\
                   hm, ' * attached:',am, ' / detached:', dm
            print 'Chunks (state dict):', len(chct.chunks), ' * active:', cht, ' / passive:', chf
            print 'DX, DY: ', self.game.world.chunks_map.DX, self.game.world.chunks_map.DY
            print 'CharX, CharY: ', self.game.world.chunks_map.charX, self.game.world.chunks_map.charY
            print 'CamX, CamY: ', self.game.world.chunks_map.camX, self.game.world.chunks_map.camY

    def cmd_teleport(self, params = []):
        """Teleportation camera of X, Y, Z

        params[0] - X
        params[1] - Y
        params[2] - Z

        if params == []
            then random X,Y,Z
        """
        if len(params) == 0:
            x = random.randint(0, self.game.world.chunks_map.size_world)
            y = random.randint(0, self.game.world.chunks_map.size_world)
            z = self.game.world.chunks_map.camZ
        elif len(params) == 1:
            z = params[0]
            x = self.game.world.chunks_map.charX
            y = self.game.world.chunks_map.charY
        else:
            try:
                x = params[0]
                y = params[1]
            except:
                return
            try:
                z = params[2]
            except:
                z = 0

        coords = int(x), int(y), int(z)
        print 'port to ', coords
        self.game.world.chunks_map.set_char_coord(coords)

    def cmd_show_tex(self, params = []):
        self.game.gui.screen_images.add_image('world_blocks',
                                            self.game.textures['world_blocks'],
                                            scale = 0.8, pos = (0, 0, 0.1))

    run_cmd = { 
                'exit': cmd_exit,
                'createmap': cmd_create_global_map,
                'create': cmd_create_global_map,
                'test': testmap,
                'write': cmd_write,
                'showmap': cmd_show_map,
                'hidemap': cmd_hide_map,
                'save': cmd_save,
                'load': cmd_load,
                'minimap': cmd_minimap,
                'seed': cmd_seed,
                'info': cmd_info,
                'showtex': cmd_show_tex,
                'teleport': cmd_teleport,
                'port': cmd_teleport,
              }
# vi: ts=4 sw=4

