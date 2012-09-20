#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Map 3d
"""

import random
import copy

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
        continents = 0
        cont_found = False
        for x in xrange(self.size):
            land_found = False
            for y in xrange(self.size):
                if self[(x, y)] > 0:
                    land_found = True
                    break
            if land_found:
                if not cont_found:
                    cont_found = True
                    continents += 1
            else:
                cont_found = False
        return continents




class Generate_Heights():
    """
    docstring for Generate_Heights
    """
    def __init__(self, map2d, seed):
        """
        docstring for __init__
        """
        self.map3d = Map3d(map2d.size, map2d.copy())
        random.seed(seed)

    def start(self):
        """
        docstring for start
        """
        yield 0, 'GO!!!!'
        land_size = self.map3d.get_land_size()
        cont_count = self.map3d.get_cont_count()
        yield 0, 'size {0}, conts: {1}'.format(land_size, cont_count)


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

# vi: ft=python:tw=0:ts=4

