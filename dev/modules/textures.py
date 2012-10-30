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
        self.map_size = 16
        self.map_len = 0
        self.map_coords = []
        self.create_map_coords()

    def create_map_coords(self):
        du = 1. / self.map_size
        dv = 1. / self.map_size
        d_uv = 0.0005
        for u in xrange(self.map_size):
            for v in xrange(self.map_size):
                coord = u * du + d_uv, v * dv + d_uv, (u + 1) * du - d_uv, (v + 1) * dv  - d_uv
                self.map_coords.append(coord)
                self.map_len += 1

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
        size = d * self.map_size
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

    def get_block_uv(self, id):
        # u1, v1, u2, v2
        # default - sand
        # 16 * 16, d_uv
        tex_coord = self.map_coords[self.map_len - self.map_size]
        if id == 'grass':
            tex_coord = self.map_coords[self.map_len - self.map_size + 1]
        elif id == 'dirt_grass':
            tex_coord = self.map_coords[self.map_len - self.map_size + 2]
        elif id == 'stone':
            tex_coord = self.map_coords[self.map_len - self.map_size + 3]
        elif id == 'snow':
            tex_coord = self.map_coords[self.map_len - self.map_size + 4]

        return tex_coord

    def load_all(self):
        self.make_blocks_texmap()
        self['sight'] = loader.loadTexture('res/textures/sight.png')

        self['water'] = loader.loadTexture("res/textures/water.png")

        self['tree'] = loader.loadTexture("res/textures/tree.png")
        self['leaf'] = loader.loadTexture("res/textures/leaf.png")


# vi: ft=python:tw=0:ts=4

