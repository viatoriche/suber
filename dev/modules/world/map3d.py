#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Map 3d
"""

import random
import copy
from PIL import Image

class Map3d(dict):
    """
    docstring for Map3d
    """
    def __init__(self, size, *args, **params):
        """
        docstring for __init__
        """
        dict.__init__(self, *args, **params)
        self.size = size

    def fill(self):
        """
        docstring for fill
        """
        for x in xrange(self.size):
            for y in xrange(self.size):
                self[(x,y)] = 0

    def get_land_size(self):
        size = 0
        for type_land in self.values():
            if type_land > 0:
                size += 1
        return size

    def get_cont_count(self):
        continents = []
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self[(x, y)] > 0:
                    land_found = True
                    break
        return continents

    def create_image(self, filename):
        """
        Create image of map and save to filename
        """
        size = self.size
        image = Image.new("RGB", (size, size), (0,0,0,0))
        for coords in self:
            # water
            if self[coords] <= 0:
                image.putpixel(coords, (0, 0, self[coords]+256))
            # land
            else:
                image.putpixel(coords, (0, self[coords], 0))
        image.save(filename, 'PNG')
        del image

    def create_height_map(self, filename):
        """
        Create image of map and save to filename
        """
        size = self.size
        image = Image.new("RGB", (size, size), (0,0,0,0))
        for coords in self:
            image.putpixel(coords, (self[coords]+128, self[coords]+128, self[coords]+128))
        image.save(filename, 'PNG')
        del image


    def gen_random_heights(self):
        """
        docstring for gen_random_heights
        """
        for coords in self:
            if self[coords] == 0:
                self[coords] = random.randint(self[coords]-128, self[coords])
            if self[coords] == 1:
                self[coords] = random.randint(self[coords], self[coords]+128)

class Generate_Heights():
    """
    docstring for Generate_Heights
    """
    def __init__(self, map2d, seed):
        """
        docstring for __init__
        """
        self.map3d = Map3d(map2d.size, map2d.copy())
        self.seed = seed

    def start(self):
        """
        docstring for start
        """
        random.seed(self.seed)
        yield 0, 'GO!!!!'
        land_size = self.map3d.get_land_size()
        yield 0, 'size of planet: {0}, size of land: {1}, '\
                 'size of water: {2}'.format(self.map3d.size ** 2,
                                             land_size,
                                             self.map3d.size ** 2 - land_size)

        self.map3d.gen_random_heights()


if __name__ == '__main__':
    maps = __import__('maps')
    iters = 5
    seed = 6754
    gen2d = maps.Map_generator_2D(seed = seed, iters = iters)
    for i, desc in gen2d.start():
        print i, desc
    print gen2d.maps.get_ascii(3)
    gen_heights = Generate_Heights(map2d = gen2d.maps[iters], seed = seed)
    for i, desc in gen_heights.start():
        print i, desc

    gen_heights.map3d.create_image('/tmp/3dmap.png')
    gen_heights.map3d.create_height_map('/tmp/heightmap.png')

# vi: ft=python:tw=0:ts=4

