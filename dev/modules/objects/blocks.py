#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Viator (viator@via-net.org)
# License:      GPL (see http://www.gnu.org/licenses/gpl.txt)
"""Block - walls, floors"""

from modules.objects.substantions import Substantion

class Block(Substantion):

    def __init__(self, game, id, top_tex, left_tex, right_tex, front_tex, back_tex, bottom_tex):
        self.top_tex = top_tex
        self.left_tex = left_tex
        self.right_tex = right_tex
        self.front_tex = front_tex
        self.back_tex = back_tex
        self.bottom_tex = bottom_tex
        Substantion.__init__(self, game, id)

    def get_top_uv(self):
        return self.game.textures.get_block_uv(self.top_tex)

    def get_left_uv(self):
        return self.game.textures.get_block_uv(self.left_tex)

    def get_right_uv(self):
        return self.game.textures.get_block_uv(self.right_tex)

    def get_front_uv(self):
        return self.game.textures.get_block_uv(self.front_tex)

    def get_back_uv(self):
        return self.game.textures.get_block_uv(self.back_tex)

    def get_bottom_uv(self):
        return self.game.textures.get_block_uv(self.bottom_tex)

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
            top_tex = 'grass'
        elif z >= config.low_mount_level[0] and z <= config.low_mount_level[1]:
            id = 'dirt_grass'
        elif z >= config.mid_mount_level[0] and z <= config.mid_mount_level[1]:
            id = 'stone'
        elif z >= config.high_mount_level[0]:
            id = 'snow'

        top_tex = id
        left_tex = id
        right_tex = id
        front_tex = id
        back_tex = id
        bottom_tex = id
        return Block(self.game, id, top_tex, left_tex, right_tex, front_tex, back_tex, bottom_tex)


# vi: ts=4 sw=4

