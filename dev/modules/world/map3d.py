#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Map 3d
"""

import random
import copy
import sys
from PIL import Image

class Map3d(dict):
    """
    docstring for Map3d
    """
    def __init__(self, size, seed, *args, **params):
        """
        docstring for __init__
        """
        dict.__init__(self, *args, **params)
        self.size = size
        self.water_z = 0
        self.seed = seed
        # 16x16 [n, m] = seed
        self.land_seeds = {}

    def fill(self):
        """
        docstring for fill
        """
        for x in xrange(self.size):
            for y in xrange(self.size):
                self[(x,y)] = self.min_z

    def get_land_size(self):
        size = 0
        for type_land in self.values():
            if type_land > self.water_z:
                size += 1
        return size

    # TODO: create!
    def get_cont_count(self):
        continents = []
        #for x in xrange(self.size):
            #for y in xrange(self.size):
                #if self[(x, y)] > 0:
                    #land_found = True
                    #break
        return continents

    def create_image(self, filename):
        """
        Create image of map and save to filename
        """
        size = self.size
        image = Image.new("RGB", (size, size), (0,0,0,0))
        for coords in self:
            # water
            if self[coords] <= self.water_z:
                image.putpixel(coords, (0, 0, 128+(self[coords])))
            # land
            elif self[coords] > self.water_z:
                image.putpixel(coords, (0, 128+(self[coords]), 0))
        image.save(filename, 'PNG')
        del image

    def create_height_map(self, filename):
        """
        Create image of map and save to filename
        """
        size = self.size
        image = Image.new("RGB", (size, size), (0,0,0,0))
        for coords in self:
            val = 128+self[coords]
            image.putpixel(coords, (val, val, val))
        image.save(filename, 'PNG')
        del image


    def get_round_xy_land(self, target_coord, start = -1):
        """
        Get NxM square, where target location in center
            target_coord = (targ_x, targ_y) or [targ_x, targ_y]
            size = size of target map

            return:
                list of [(x1, y1)...(x3, y3)]
        """
        targ_x, targ_y = target_coord
        coords = []
        size = self.size
        end = abs(start)+1
        # from -1/-1 to 1/1
        for iter_x in xrange(start, end):
            round_x = iter_x
            if iter_x < 0:
                round_x = size+iter_x
            if iter_x > size-1:
                round_x = size-1-iter_x
            for iter_y in xrange(start, end):
                round_y = iter_y
                if iter_y < 0:
                    round_y = size+iter_y
                if iter_y > size-1:
                    round_y = size-1-iter_y

                coords.append((round_x, round_y))

        return coords


    def gen_random_heights(self):
        """
        docstring for gen_random_heights
        """

        random.seed(self.seed)
        def diamond_it(sx, sy, size):
            #print sx, sy, sx+size-1, sy+size-1, size
            dsize = size/2
            if dsize <= 0:
                return
            ex = sx+size-1
            ey = sy+size-1
            # lets get math style

            A = sx, sy
            B = ex, sy
            C = sx, ey
            D = ex, ey
            E = sx+dsize, sy+dsize
            F = sx, sy + dsize
            G = sx + dsize, sy
            H = ex, sy + dsize
            I = sx + dsize, ey

            def RAND(X):
                z = self[X]
                if z <= self.water_z:
                    return random.randint(-1, 0)
                else:
                    return random.randint(0, 1)

            self[E] = (self[A] + self[B] + self[C] + self[D]) / 4 + RAND(E)

            self[F] = (self[A] + self[C] + self[E] + self[E]) / 4 + RAND(F)
            self[G] = (self[A] + self[B] + self[E] + self[E]) / 4 + RAND(G)
            self[H] = (self[B] + self[D] + self[E] + self[E]) / 4 + RAND(H)
            self[I] = (self[C] + self[D] + self[E] + self[E]) / 4 + RAND(I)

            diamond_it(A[0], A[1], dsize)
            diamond_it(G[0], G[1], dsize)
            diamond_it(F[0], F[1], dsize)
            diamond_it(E[0], E[1], dsize)

        diamond_it(0, 0, self.size)

        #for coords in self:
            #col = 0
            #xy_rounds = self.get_round_xy_land(coords, -1)
            #for round_coords in xy_rounds:
                #col += self[round_coords]
            #self[coords] = int(round(col/float(len(xy_rounds))))

        for x in xrange(16):
            for y in xrange(16):
                self.land_seeds[x,y] = random.randint(0, sys.maxint)

def map2d_to_3d(map2d, seed):
    """docstring for map2d_to_3d

    """
    map3d = Map3d(map2d.size, seed)
    for coords in map2d:
        # if water
        mount = random.randint(0, map2d.size)
        if mount == map2d.size:
            mount = 1
        elif mount == 0:
            mount = -1
        else:
            mount = 0
        if map2d[coords] == 0:
            map3d[coords] = map3d.water_z+mount
        else:
            map3d[coords] = map3d.water_z+1+mount
    for x in xrange(16):
        for y in xrange(16):
            map3d.land_seeds[x, y] = random.randint(0, sys.maxint)
    return map3d


class Generate_Heights():
    """
    docstring for Generate_Heights
    """
    def __init__(self, map3d, start_x, start_y):
        """
        docstring for __init__
        """
        seed = map3d.land_seeds[start_x, start_y]
        self.map3d = Map3d(map3d.size, seed)
        for x in xrange(start_x, start_x + 16):
            sx = (x - start_x) * 16
            for y in xrange(start_y, start_y + 16):
                sy = (y - start_y) * 16
                dx = sx + 16
                dy = sy + 16
                for my_x in xrange(sx, dx):
                    for my_y in xrange(sy, dy):
                        if map3d[(x, y)] <= map3d.water_z:
                            self.map3d[(my_x, my_y)] = map3d[(x,y)-4]
                        else:
                            self.map3d[(my_x, my_y)] = map3d[(x,y)+4]

    def start(self):
        """
        docstring for start
        """
        yield 0, 'GO!!!!'
        land_size = self.map3d.get_land_size()
        yield 0, 'size of planet: {0}, size of land: {1}, '\
                 'size of water: {2}'.format(self.map3d.size ** 2,
                                             land_size,
                                             self.map3d.size ** 2 - land_size)

        self.map3d.gen_random_heights()


if __name__ == '__main__':
    maps = __import__('map2d')
    iters = 5
    seed = 6754
    random.seed(seed)
    gen2d = maps.Map_generator_2D(iters = iters)
    for i, desc in gen2d.start():
        print i, desc
    print gen2d.maps.get_ascii(3)
    print 'size line: ', gen2d.maps[iters].size
    main3d = map2d_to_3d(gen2d.maps[iters], seed)
    for x in xrange(0, 2):
        for y in xrange(0, 2):
            gen_heights = Generate_Heights(main3d, x * 16, y * 16)
            for i, desc in gen_heights.start():
                print i, desc
            gen_heights.map3d.create_height_map('/tmp/maps/{0}_{1}_3dmap.png'.format(x, y))

# vi: ft=python:tw=0:ts=4

