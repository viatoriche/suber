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


    def get_round_xy_land(self, target_coord, start = -1, toroid = True):
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
        # random maps is not toroid
#        if not toroid:
            #if end > size:
                #end = size
            #if start <0:
                #start = 0

        # from -1/-1 to 1/1
        for iter_x in xrange(start, end):
            round_x = iter_x + targ_x
            if round_x < 0:
                if toroid:
                    round_x = size+iter_x
                else:
                    round_x = 0
            if round_x > size - 1:
                if toroid:
                    round_x = size - 1 -iter_x
                else:
                    round_x = size - 1
            for iter_y in xrange(start, end):
                round_y = iter_y + targ_y
                if round_y < 0:
                    if toroid:
                        round_y = size+iter_y
                    else:
                        round_y = 0
                if round_y > size - 1:
                    if toroid:
                        round_y = size - 1 - iter_y
                    else:
                        round_y = size - 1

                if (round_x, round_y) not in coords:
                    coords.append((round_x, round_y))

        return coords

    # return 0 - water, 1 - land
    def is_type(self, coords):
        """return 0 - if water, 1 - if land
        """
        if self[coords] <= self.water_z:
            return 0
        else:
            return 1

    def get_all_coasts(self):
        """Get coordinates of all coast-point of map

            return list of coordinates:
               [(x1,y1),(x2,y2)...(xN,yN)]
        """
        coasts = []
        land = []
        water = []

        for coord in self:
            if self.is_type(coord) == 1:
                land.append(coord)

        for coord in self:
            if self.is_type(coord) == 0:
                water.append(coord)

        if len(land) == 0 or len(water) == 0:
            return coasts

        if len(land) < len(water):
            target = land
            search_target = 0
        else:
            target = water
            search_target = 1

        for coord in target:
            # get coordinates around this point
            round_coords = self.get_round_xy_land(coord, -1, False)
            for r_coord in round_coords:
                if self.is_type(r_coord) == search_target:
                    coasts.append(coord)
                    break
        return coasts

    def gen_random_heights(self):
        """
        docstring for gen_random_heights

        TODO: lands + lands smooth problem
        """
        import time
        random.seed(self.seed)
        # coast smooth

        def create_smooth_patterns(count):
            patterns = []
            for i in xrange(count):
                pattern = [(0, 0)]
                j = 0
                while j <= 256:
                    x, y = pattern[(random.randint(0, len(pattern)-1))]
                    x += random.randint(-1, 1)
                    y += random.randint(-1, 1)
                    if (x, y) not in pattern:
                        pattern.append((x, y))
                        j += 1
                patterns.append(pattern)
            return patterns

        t = time.time()
        smooth_patterns = create_smooth_patterns(64)
        print 'create patterns: ', time.time() - t

        def smooth_it(rounds, center):
            smooth_pattern = smooth_patterns[random.randint(0, len(smooth_patterns)-1)]
            cx, cy = center
            for x, y in smooth_pattern:
                self[cx+x, cy+y] = self[center]

        # get and smooth coasts from water
        t = time.time()
        coasts = self.get_all_coasts()
        print 'get coasts: ', time.time() - t
        t = time.time()
        for coord in coasts:
            rounds = self.get_round_xy_land(coord, -8, False)
            smooth_it(rounds, coord)

        print 'smooth: ', time.time() - t

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
                return random.randint(-1, 2)

            ### for coasts dont disappear

            def normalize(add_z, X):
                if self[X] <= self.water_z:
                    if add_z > self.water_z:
                        add_z = random.randint(-1,0)
                else:
                    if add_z <= self.water_z:
                        add_z = random.randint(1,2)
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

        t = time.time()
        diamond_it(0, 0, self.size)
        print 'diamond: ', time.time() - t
        #diamond_it(0, 0, self.size)
        #diamond_it(0, 0, self.size)
        #diamond_it(0, 0, self.size)

        # alias
        #for tar_coord in self:
            #average = 0
            #rounds = self.get_round_xy_land(tar_coord, -1, False)
            #for coord in rounds:
                #average += self[coord]
            #self[coord] = int(round(average / float(len(rounds))))

        for x in xrange(16):
            for y in xrange(16):
                self.land_seeds[x,y] = random.randint(0, sys.maxint)

def map2d_to_3d(map2d, seed):
    """docstring for map2d_to_3d

    """
    map3d = Map3d(map2d.size, seed)
    for coords in map2d:
        # if water
        if map2d[coords] == 0:
            map3d[coords] = map3d.water_z
        else:
            map3d[coords] = map3d.water_z+1

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
    print 'generate heights started in: ', start_x, start_y
    for x in xrange(map3d.size):
        for y in xrange(map3d.size):
            sx = (x / 16) + (start_x * 16)
            sy = (y / 16) + (start_y * 16)
            # heights
            height = source_map[(sx, sy)]
            if height == source_map.water_z or height == source_map.water_z + 1:
                map3d[(x, y)] = height
            else:
                if height < source_map.water_z:
                    map3d[(x, y)] = height - 1
                else:
                    map3d[(x, y)] = height + 1
            #map3d[(x, y)] = source_map[(sx, sy)]

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

