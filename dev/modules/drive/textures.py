#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Textures modul
"""
from pandac.PandaModules import Texture, PNMImage

class TextureCollection(dict):
    """
    docstring for TextureCollention
    """
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
        #char_x, char_y, char_z = map_tree.coords
        #char_x = char_x / factor
        #char_y = char_y / factor
        #image.setPixel(char_x, char_y, (255, 0, 0))
        #if factor>2:
            #image.setPixel(char_x, char_y, (255, 0, 0))
        #else:
            #for x in xrange(char_x - 1, char_x+2):
                #cx = x
                #if cx > size-1: cx = size-1
                #if cx < 0: cx = 0
                #for y in xrange(char_y - 1, char_y+2):
                    #cy = y
                    #if cy > size-1: cy = size-1
                    #if cy < 0: cy = 0
                    #image.setPixel(cx, cy, (255, 0, 0))
        texture = Texture()
        texture.load(image)
        return texture

textures = TextureCollection()
# vi: ft=python:tw=0:ts=4

