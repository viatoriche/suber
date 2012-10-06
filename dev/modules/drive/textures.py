#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Textures modul
"""
from pandac.PandaModules import Texture, PNMImage
from config import Config

class TextureCollection(dict):
    """
    docstring for TextureCollention
    """
    config = Config()
    def __init__(self):
        dict.__init__(self)
        self.make_blocks_texmap()

    def get_map_2d_tex(self, map2d, factor = 1):
        """Generate texture for map2d, factor - for size [size / factor]
        """
        size = map2d.size / factor
        image = PNMImage(size, size)
        for x in xrange(size):
            for y in xrange(size):
                px = x * factor
                py = y * factor
                if map2d[(px, py)] <= map2d.water_z:
                    image.setPixel(x, y, (0, 0, 100))
                else:
                    image.setPixel(x, y, (0, 100, 0))
        texture = Texture()
        texture.load(image)
        return texture

    def get_map_3d_tex(self, world, size):
        """Generate texture for map2d, factor - for size [size / factor]
        """
        size_world = world.config.size_world
        mod = size_world / size
        image = PNMImage(size, size)
        for x in xrange(size):
            for y in xrange(size):
                px = x * mod
                py = y * mod
                height = world.map_3d[px, py]
                color = (abs(height) / 50) + 50
                if color > 255:
                    color = 255
                if height <= 0:
                    image.setPixel(x, y, (0, 0, 255-color))
                else:
                    image.setPixel(x, y, (0, color, 0))

        image.write('/tmp/{0}.png'.format(size))
        texture = Texture()
        texture.load(image)
        return texture


    def make_blocks_texmap(self):
        image_sand = PNMImage('res/textures/sand.png')
        image_land = PNMImage('res/textures/land.png')
        image_low = PNMImage("res/textures/low_mount.png")
        image_mid = PNMImage("res/textures/mid_mount.png")
        image_high = PNMImage("res/textures/high_mount.png")
        d = image_sand.getReadXSize()
        size = d * 4
        image_all = PNMImage(size, size)
        image_all.copySubImage(image_sand, 0, 0)
        image_all.copySubImage(image_land, d, 0)
        image_all.copySubImage(image_low, d * 2, 0)
        image_all.copySubImage(image_mid, d * 3, 0)
        image_all.copySubImage(image_high, 0, d)
        self['world_blocks'] = Texture()
        self['world_blocks'].load(image_all)
        self['world_blocks'].setMagfilter(Texture.FTLinearMipmapLinear)
        self['world_blocks'].setMinfilter(Texture.FTLinearMipmapLinear)
        self['world_blocks'].setWrapU(Texture.WMRepeat)
        self['world_blocks'].setWrapV(Texture.WMRepeat)

    def get_block_uv_height(self, z):
        # u1, v1, u2, v2
        tex_coord = 0.0, 1.0, 0.25, 0.75
        if z >= self.config.land_mount_level[0] and z <= self.config.land_mount_level[1]:
            tex_coord = 0.25, 1.0, 0.5, 0.75
        elif z >= self.config.low_mount_level[0] and z <= self.config.low_mount_level[1]:
            tex_coord = 0.5, 1.0, 0.75, 0.75
        elif z >= self.config.mid_mount_level[0] and z <= self.config.mid_mount_level[1]:
            tex_coord = 0.75, 1.0, 1.0, 0.75
        elif z >= self.config.high_mount_level[0]:
            tex_coord = 0.0, 0.75, 0.25, 0.5

        return tex_coord



textures = TextureCollection()
# vi: ft=python:tw=0:ts=4

