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
        start = self.map_len - self.map_size
        self.block_number = {
                'sand': start,
                'grass': start + 1,
                'dirt_grass': start + 2,
                'stone': start + 3,
                'snow': start + 4,
                'tech_top': start + 5,
                'tech_left': start + 6,
                'tech_right': start + 7,
                'tech_front': start + 8,
                'tech_back': start + 9,
            }

    def create_map_coords(self):
        du = 1. / self.map_size
        dv = 1. / self.map_size
        d_uv = 0.0005
        for u in xrange(self.map_size):
            for v in xrange(self.map_size):
                coord = u * du + d_uv, v * dv + d_uv, (u + 1) * du - d_uv, (v + 1) * dv  - d_uv
                self.map_coords.append(coord)
                self.map_len += 1

    def make_blocks_texmap(self):
        images = []
        # 0 - sand
        images.append(PNMImage('res/textures/{0}sand.png'.format(
                                        Config().tex_suffix)))
        # 1 - land
        images.append(PNMImage('res/textures/{0}grass.png'.format(
                                        Config().tex_suffix)))
        # 2 - low_mount
        images.append(PNMImage("res/textures/{0}dirt_grass.png".format(
                                        Config().tex_suffix)))
        # 3 - mid_mount
        images.append(PNMImage("res/textures/{0}stone.png".format(
                                        Config().tex_suffix)))
        # 4 - high_mount
        images.append(PNMImage("res/textures/{0}snow.png".format(
                                        Config().tex_suffix)))
        # 5 - tech temp
        images.append(PNMImage("res/textures/{0}tech_top.png".format(
                                        Config().tex_suffix)))
        # 6 - tech temp
        images.append(PNMImage("res/textures/{0}tech_left.png".format(
                                        Config().tex_suffix)))
        # 7 - tech temp
        images.append(PNMImage("res/textures/{0}tech_right.png".format(
                                        Config().tex_suffix)))
        # 8 - tech temp
        images.append(PNMImage("res/textures/{0}tech_front.png".format(
                                        Config().tex_suffix)))
        # 9 - tech temp
        images.append(PNMImage("res/textures/{0}tech_back.png".format(
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
        return self.map_coords[self.block_number[id]]

    def load_all(self):
        self.make_blocks_texmap()
        self['sight'] = loader.loadTexture('res/textures/{0}sight.png'.format(
                                        Config().tex_suffix))

        self['water'] = loader.loadTexture("res/textures/{0}water.png".format(
                                        Config().tex_suffix))

        self['tree'] = loader.loadTexture("res/textures/{0}tree.png".format(
                                        Config().tex_suffix))
        self['leaf'] = loader.loadTexture("res/textures/{0}leaf.png".format(
                                        Config().tex_suffix))


# vi: ft=python:tw=0:ts=4

