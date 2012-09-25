#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Map 3d
"""

import random
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
                return random.randint(-2, 2)

            ### for coasts dont disappear

            if self.water_z != 0:
                print 'WATER: ', self.water_z
            def normalize(add_z, X):
                if self[X] <= self.water_z:
                    if add_z > self.water_z:
                        add_z = 0 - add_z
                else:
                    if add_z <= self.water_z:
                        add_z = 1 - add_z
                return add_z

            ### E

            add_z = ((self[A] + self[B] + self[C] + self[D]) / 4) + RAND(E)

            self[E] = normalize(add_z, E)

            ### F

            add_z = (self[A] + self[C] + self[E] + self[E]) / 4 + RAND(F)

            self[F] = normalize(add_z, F)

            ### G

            add_z = (self[A] + self[B] + self[E] + self[E]) / 4 + RAND(G)

            self[G] = normalize(add_z, G)

            ### H

            add_z = (self[B] + self[D] + self[E] + self[E]) / 4 + RAND(H)

            self[H] = normalize(add_z, H)

            ### I
            add_z = (self[C] + self[D] + self[E] + self[E]) / 4 + RAND(I)

            self[I] = normalize(add_z, I)

            ### Start recurse for diamond alg
            diamond_it(A[0], A[1], dsize)
            diamond_it(G[0], G[1], dsize)
            diamond_it(F[0], F[1], dsize)
            diamond_it(E[0], E[1], dsize)

        diamond_it(0, 0, self.size)
        # TODO: create alias coasts

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


def generate_heights(source_map, start_x, start_y):
    """
    docstring for generate_heights
    """
    #import pdb; pdb.set_trace()
    seed = source_map.land_seeds[start_x, start_y]
    map3d = Map3d(source_map.size, seed)
    for x in xrange(map3d.size):
        for y in xrange(map3d.size):
            sx = (x / 16) + (start_x * 16)
            sy = (y / 16) + (start_y * 16)
            if source_map[(sx, sy)] <= source_map.water_z:
                map3d[(x, y)] = source_map[(sx, sy)] - 1
            else:
                map3d[(x, y)] = source_map[(sx, sy)] + 1

    map3d.gen_random_heights()
    return map3d

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
    map3d = generate_heights(main3d, 5, 5)
    map3d.create_image('/tmp/maps/{0}_{1}_3dmap.png'.format(0, 0))

# vi: ft=python:tw=0:ts=4

