#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
3D map with perlin algorithm
"""

import sys
import random
from pandac.PandaModules import PerlinNoise2
from PIL import Image

class Map3d(dict):
    """Class for map with heights

       Keys: (X, Y)
       Values = Heights
    """
    # World size 64 ** 4, in meters
    world_size = 16777216
    # when level = 18. len_cube = 1 meter, x = x, y = y
    # when level = 1, len_cube = 
    def __init__(self, map2d, seed, size, *args, **params):
        dict.__init__(self, *args, **params)
        self.map2d = map2d
        self.seed = seed
        self.mod = self.world_size / self.map2d.size
        self.perlins = {}
        random.seed(seed)
        # generate octaves
        for x in xrange(1, 6):
            seed = random.randint(0, sys.maxint)
            self.perlins[x] = (PerlinNoise2(sx = self.world_size, sy = self.world_size,
                                   table_size = self.world_size, seed = seed))
            self.perlins[x].setScale(32000 / (x**5) )

# deprecated, because level - dont need
#    def get_height(self, x, y):
        #"""return height for x, y with level

        #lol, level - dont need
        #level - deprecated
        #"""
        #mod = 1.0 / level
        #height = self[x, y]
        #return height

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
        #x, y = item
        #x = abs(x)
        #y = abs(y)
        if item in self:
            return dict.__getitem__(self, item)
        else:
            # generate perlin height
            #print 'item: ', x, y
            x, y = item

            #height = self.map2d[int(x/self.mod), int(y/self.mod)]
            #if height == 0:
                #height = -10000
            #else:
                #height = 10000

            height = 0

            for level in self.perlins:
                height += self.perlins[level](x, y) * (10000 / level**5)

            self[x, y] = int(height)
            return height

            #height = self.map2d[x/mod, y/mod]
            #self[x, y] = height
            #return height


if __name__ == "__main__":
    maps = __import__('map2d')
    gen = maps.Map_generator_2D(iters = 3)
    for i, desc in gen.start():
        pass

    print gen.maps.get_ascii(i)
    map2d = gen.end_map


# vi: ft=python:tw=0:ts=4

