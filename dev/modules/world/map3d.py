#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
3D map with perlin algorithm
"""

import random
from pandac.PandaModules import PerlinNoise2
from PIL import Image

class Map3d(dict):
    """Class for map with heights

       Keys: (X, Y)
       Values = Heights
    """
    def __init__(self, map2d, seed, size, *args, **params):
        dict.__init__(self, *args, **params)
        self.map2d = map2d
        self.seed = seed
        self.perlin = PerlinNoise2(sx = size, sy = size, seed = seed)
        self.perlin.setScale(20)

    def get_height_place(self, x, y, level):
        """return height for x, y with level

        x .. level * x, y ..level *y
        """
        heights = 0.0
        count = 0.0
        for x in xrange(x, x*level):
            for y in xrange(y, y*level):
                heights += self[x, y]
                count += 1.0
        height = int(round(heights/count))

    def create_image(self, x, y, size, level, filename):
        """Generate image with heights
        """
        image1 = Image.new("RGB", (size, size), (0, 0, 0, 0))
        for x in xrange(x, size):
            for y in xrange(y, size):
                pass

    def __getitem__(self, item):
        """If item not in dict, when perlin generate and return
        """
        if item in self:
            return dict.__getitem__(self, item)
        else:
            # generate perlin height
            x, y = item
            self[x, y] = int(self.perlin(x, y) * 10000)
            return self[x, y].get( (x, y) )


if __name__ == "__main__":
    maps = __import__('map2d')
    gen = maps.Map_generator_2D(iters = 3)
    for i, desc in gen.start():
        pass

    print gen.maps.get_ascii(i)
    map2d = gen.end_map


# vi: ft=python:tw=0:ts=4

