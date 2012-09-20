#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""

from pandac.PandaModules import Texture, PNMImage

class World():
    """
    docstring for World
    """
    map_2d = None


def generate_map_texture(map_world):
    size = map_world.size
    image = PNMImage(size, size)
    image.fill(0,0,0)
    for x, y in map_world:
        if map_world[(x,y)] == 0:
            image.setPixel(x, y, (0, 0, 128))
        else:
            image.setPixel(x, y, (0, 200, 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

