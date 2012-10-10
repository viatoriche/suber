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
    def __init__(self, game):
        dict.__init__(self)
        self.game = game

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


    def make_blocks_texmap(self):
        images = []
        # 0 - sand
        images.append(PNMImage('res/textures/{0}sand.png'.format(
                                        Config().tex_suffix)))
        # 1 - land
        images.append(PNMImage('res/textures/{0}land.png'.format(
                                        Config().tex_suffix)))
        # 2 - low_mount
        images.append(PNMImage("res/textures/{0}low_mount.png".format(
                                        Config().tex_suffix)))
        # 3 - mid_mount
        images.append(PNMImage("res/textures/{0}mid_mount.png".format(
                                        Config().tex_suffix)))
        # 4 - high_mount
        images.append(PNMImage("res/textures/{0}high_mount.png".format(
                                        Config().tex_suffix)))
        d = images[0].getReadXSize()
        # 16 x 16 textures
        size = d * 16
        image_all = PNMImage(size, size)
        n = 0
        for i in xrange(0, size, d):
            for j in xrange(0, size, d):
                image_all.copySubImage(images[n], j, i)
                n += 1
                if n >= len(images):
                    break
            if n >= len(images):
                break

        self['world_blocks'] = Texture()
        self['world_blocks'].load(image_all)
        self['world_blocks'].setMagfilter(Texture.FTLinearMipmapLinear)
        self['world_blocks'].setMinfilter(Texture.FTLinearMipmapLinear)

    def get_block_uv_height(self, z):
        # u1, v1, u2, v2
        config = self.game.vox_config
        tex_coord = 0.0, 1.0, 0.0625, 0.9375
        if z >= config.land_mount_level[0] and z <= config.land_mount_level[1]:
            tex_coord = 0.0625, 1.0, 0.125, 0.9375
        elif z >= config.low_mount_level[0] and z <= config.low_mount_level[1]:
            tex_coord = 0.125, 1.0, 0.1875, 0.9375
        elif z >= config.mid_mount_level[0] and z <= config.mid_mount_level[1]:
            tex_coord = 0.1875, 1.0, 0.25, 0.9375
        elif z >= config.high_mount_level[0]:
            tex_coord = 0.25, 1.0, 0.3125, 0.9375

        return tex_coord

    def load_all(self):
        self.make_blocks_texmap()
        self['sight'] = loader.loadTexture('res/textures/sight.png')

        self['water'] = loader.loadTexture("res/textures/water.png")
        #self['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        #self['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        #self['black'] = loader.loadTexture("res/textures/black.png")
        self['tree'] = loader.loadTexture("res/textures/tree.png")
        self['leaf'] = loader.loadTexture("res/textures/leaf.png")
        #self['black'].setMagfilter(Texture.FTLinearMipmapLinear)
        #self['black'].setMinfilter(Texture.FTLinearMipmapLinear)



#textures = TextureCollection()
# vi: ft=python:tw=0:ts=4

