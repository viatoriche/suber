#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Block - walls, floors"""

from modules.objects.substantions import Substantion

class Block(Substantion):

    def get_top_uv(self):
        return self.game.textures.get_block_uv(self.id)

    def get_uv(self):
        return self.game.textures.get_block_uv(self.id)

class CoordBlock():
    def __init__(self, game, config):
        self.game = game
        self.config = config

    def __call__(self, coord):
        """TODO: add x,y depend
        """
        config = self.config
        id = 'sand'
        x, y, z = coord
        if z >= config.land_mount_level[0] and z <= config.land_mount_level[1]:
            id = 'grass'
        elif z >= config.low_mount_level[0] and z <= config.low_mount_level[1]:
            id = 'dirt_grass'
        elif z >= config.mid_mount_level[0] and z <= config.mid_mount_level[1]:
            id = 'stone'
        elif z >= config.high_mount_level[0]:
            id = 'snow'

        return Block(self.game, id)


# vi: ts=4 sw=4

