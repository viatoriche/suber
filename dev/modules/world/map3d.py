#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Map 3d
"""

import random
import sys
from config import Config

from PIL import Image

class Map3d(dict):
    """
    docstring for Map3d
    """
    config = Config()
    map_x = 0
    map_y = 0
    def __init__(self, map_tree, size, seed, first = True, *args, **params):
        """
        docstring for __init__

        mount_level = 0 land
        1 - low level
        2 - mid level
        3 - high level
        """
        dict.__init__(self, *args, **params)
        random.seed(seed)
        sys.setrecursionlimit(150000)
        self.size = size
        self.water_z = 0
        self.seed = seed
        self.map_tree = map_tree
        # mode x mode [n, m] = seed
        self.land_seeds = {}
        self.mount_levels = {}
        if first:
            for x in xrange(0, size):
                for y in xrange(0, size):
                    dice = random.randint(0, 100)
                    if dice <= self.config.factor_high_mount:
                        self.mount_levels[(x, y)] = self.config.high_mount_level
                    elif dice > self.config.factor_high_mount and dice <= self.config.factor_mid_mount:
                        self.mount_levels[(x, y)] = self.config.mid_mount_level
                    elif dice > self.config.factor_mid_mount and dice <= self.config.factor_low_mount:
                        self.mount_levels[(x, y)] = self.config.low_mount_level
                    else:
                        self.mount_levels[(x, y)] = self.config.land_mount_level

        for x in xrange(self.config.factor):
            for y in xrange(self.config.factor):
                self.land_seeds[x,y] = random.randint(0, sys.maxint)

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


    def get_round_xy_land(self, target_coord, start = -1, fact_borders = True):
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
            round_x = iter_x + targ_x
            if round_x < 0:
                if fact_borders:
                    round_x = 0
            if round_x > size - 1:
                if fact_borders:
                    round_x = size - 1
            for iter_y in xrange(start, end):
                round_y = iter_y + targ_y
                if round_y < 0:
                    if fact_borders:
                        round_y = 0
                if round_y > size - 1:
                    if fact_borders:
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

    def get_all_coasts(self, start, size):
        """Get coordinates of all coast-point of map

            return list of coordinates:
               [(x1,y1),(x2,y2)...(xN,yN)]
        """
        coasts = []
        land = []
        water = []
        start = start - 1
        size = size + (start * 2)
        start = -start

        coords = []
        for x in xrange(start, size):
            for y in xrange(start, size):
                coords.append( (x, y) )

        for coord in coords:
            if self.is_type(coord) == 1:
                land.append(coord)

        for coord in coords:
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
            x, y = coord

            #if x>self.config.factor_tor: continue
            #if y>self.config.factor_tor: continue
            #if x<0: continue
            #if y<0: continue

            # get coordinates around this point
            round_coords = self.get_round_xy_land(coord, -1, True)
            for r_coord in round_coords:
                if self.is_type(r_coord) == search_target:
                    coasts.append(coord)
                    break
        return coasts

    def __setitem__(self, item, height):
        """Set height to other map, if x, y not in self
        """

        dict.__setitem__(self, item, height)
        x, y = item
        if x>=0 and x<=self.config.factor_double_tor and y>=0 and y<=self.config.factor_double_tor:
            pass
        else:
            if self.map_tree:
                dx, dy = 0, 0
                if x < 0:
                    dx = -1
                # if dx == -1:  <----
                elif x > self.config.factor_double_tor:
                    dx = 1
                # if dx == 1:   ---->
                if y < 0:
                    dy = -1
                # if dy == -1:   up
                elif y > self.config.factor_double_tor:
                    dy = 1
                # if dy == 1:    down

                # -8 => 63
                if x < 0:
                    x = self.config.factor_double + x
                elif x > self.config.factor_double_tor:
                    x = x - self.config.factor_double

                if y < 0:
                    y = self.config.factor_double + y
                elif y > self.config.factor_double_tor:
                    y = y - self.config.factor_double

                self.map_tree.change_cache_map_height(self.map_x + dx, self.map_y + dy, x, y, height)

    def __getitem__(self, item):
        """ If not, return from other map or 1

        for diamond_square // and align

        REMEMBER FOR DEBUG

        """
        if item in self:
            return dict.__getitem__(self, item)
        else:
            # heights from near maps

            height = None

            if self.map_tree:
                x, y = item
                dx, dy = 0, 0
                if x < 0:
                    dx = -1
                # if dx == -1:  <----
                elif x > self.config.factor_double_tor:
                    dx = 1
                # if dx == 1:   ---->
                if y < 0:
                    dy = -1
                # if dy == -1:   up
                elif y > self.config.factor_double_tor:
                    dy = 1
                # if dy == 1:    down

                # -8 => 63
                if x < 0:
                    x = self.config.factor_double + x
                elif x > self.config.factor_double_tor:
                    x = x - self.config.factor_double

                if y < 0:
                    y = self.config.factor_double + y
                elif y > self.config.factor_double_tor:
                    y = y - self.config.factor_double

                height = self.map_tree.get_cache_map_height(self.map_x + dx, self.map_y + dy, x, y)

                if height == None:
                    height = self.map_tree.get_parent_map_height(self.map_x + dx, self.map_y + dy, x, y)

            if height == None:
                x, y = item
                if x < 0:
                    x = x + self.config.factor
                elif x > self.config.factor_double_tor:
                    x = x - self.config.factor
                if y < 0:
                    y = y + self.config.factor
                elif y > self.config.factor_double_tor:
                    y = y - self.config.factor
                height = self[(x, y)]

            #self[item] = height
            return height


    def gen_random_heights(self, First = False):
        """
        docstring for gen_random_heights

        TODO: lands + lands smooth problem
        """
        import time
        random.seed(self.seed)

        # if map part was modified: change heights

        def add_heights():
            levels = self.mount_levels
            for x in xrange(0, self.size):
                for y in xrange(0, self.size):
                    if self[x, y] <= self.water_z:
                        self[x, y] = random.randint(-levels[x, y][1],
                                                    -levels[x, y][0])
                    else:
                        self[x, y] = random.randint(levels[x, y][0],
                                                    levels[x, y][1])

        def create_smooth_patterns(count):
            patterns = []
            for i in xrange(count):
                pattern = [(0, 0)]
                j = 0
                while j <= self.config.factor_double:
                    x, y = pattern[(random.randint(0, len(pattern)-1))]
                    x += random.randint(-1, 1)
                    y += random.randint(-1, 1)
                    if (x, y) not in pattern:
                        pattern.append((x, y))
                        j += 1
                patterns.append(pattern)
            return patterns

        def smooth_it(rounds, center):
            smooth_patterns = create_smooth_patterns(16)
            smooth_pattern = smooth_patterns[random.randint(0, len(smooth_patterns)-1)]
            cx, cy = center
            for x, y in smooth_pattern:
                self[cx+x, cy+y] = self[center]

        # get and smooth coasts from water
        def smooth_all_coasts():
            coasts = self.get_all_coasts(self.size, self.size)
            for coord in coasts:
                rounds = self.get_round_xy_land(coord, -self.config.factor_tor, False)
                smooth_it(rounds, coord)

        #t = time.time()
        #smooth_all_coasts()
        #print 'smooth: ', time.time() - t

        def square_diamond(sx, sy, size, strong):
            """Algorithm Square-diamond generate terrain heights

            -> http://www.lighthouse3d.com/opengl/terrain/index.php?mpd2
            """
            if size == 1:
                return

            dsize = size/2
            ex = sx+size-1
            ey = sy+size-1
            # lets get math style


            # SQUARE STEP

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
                return random.randint(-strong, strong)

            ### for coasts dont disappear

            def normalize(add_z, X):
                if self[X] <= self.water_z:
                    if add_z > self.water_z:
                        add_z = 0
                else:
                    if add_z <= self.water_z:
                        add_z = 1
                return add_z

            # Generate heights
            # E = (A+B+C+D) / 4 + RAND(d)
            # F = (A + C + E + E) / 4 + RAND(d)
            # G = (A + B + E + E) / 4 + RAND(d)
            # H = (B + D + E + E) / 4 + RAND(d)
            # I = (C + D + E + E) / 4 + RANS(d)

            ### E

            try:

                add_z = ((self[A] + self[B] + self[C] + self[D]) / 4) + RAND(E)

            except KeyError, e:
                print A, B, C, D, size, dsize, len(self)
                raise e


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


            # DIAMOND STEP

            # get coordinates
            # 0 - x, 1 - y

            x, y = 0, 1

            dx = (G[x] - A[x]) / 2
            dy = (F[y] - A[y]) / 2

            J = A[x] + dx, A[y] + dy
            K = G[x] + dx, G[y] + dy
            L = F[x] + dx, F[y] + dy
            M = E[x] + dx, E[y] + dy

            N = A[x], A[y] + dy
            O = A[x] + dx, A[y]
            P = G[x], G[y] + dy
            Q = A[x] + dx, F[y]

            # Generate Heights
            # J = (A + G + F + E)/4 + RAND(d)
            # K = (G + B + E + H)/4 + RAND(d)
            # L = (F + E + C + I)/4 + RAND(d)
            # M = (E + H + I + D)/4 + RAND(d)

            # J
            add_z = ((self[A] + self[G] + self[F] + self[E]) / 4) + RAND(J)
            self[J] = normalize(add_z, J)

            # K
            add_z = ((self[G] + self[B] + self[E] + self[H]) / 4) + RAND(K)
            self[K] = normalize(add_z, K)

            # L
            add_z = ((self[F] + self[E] + self[C] + self[I]) / 4) + RAND(L)
            self[L] = normalize(add_z, L)

            # M
            add_z = ((self[E] + self[H] + self[I] + self[D]) / 4) + RAND(M)
            self[M] = normalize(add_z, M)

            # N = (K + A + J + F)/4 + RAND(d)
            # O = (L + A + G + J)/4 + RAND(d)
            # P = (J + G + K + E)/4 + RAND(d)
            # Q = (F + J + E + L)/4 + RAND(d)

            # N
            add_z = ((self[K] + self[A] + self[J] + self[F]) / 4) + RAND(N)
            self[N] = normalize(add_z, N)

            # O
            add_z = ((self[L] + self[A] + self[G] + self[J]) / 4) + RAND(O)
            self[O] = normalize(add_z, O)

            # P
            add_z = ((self[J] + self[G] + self[K] + self[E]) / 4) + RAND(P)
            self[P] = normalize(add_z, P)

            # Q
            add_z = ((self[F] + self[J] + self[E] + self[L]) / 4) + RAND(Q)
            self[Q] = normalize(add_z, Q)

            # N = (A + J + F)/3 + RAND(d)
            # O = (A + G + J)/3 + RAND(d)

            # N
            add_z = ((self[A] + self[J] + self[F]) / 3) + RAND(N)
            self[N] = normalize(add_z, N)

            # O
            add_z = ((self[A] + self[G] + self[J]) / 3) + RAND(N)
            self[O] = normalize(add_z, O)


            ### Start recurse for diamond alg
            square_diamond(A[0], A[1], dsize, strong)
            square_diamond(G[0], G[1], dsize, strong)
            square_diamond(F[0], F[1], dsize, strong)
            square_diamond(E[0], E[1], dsize, strong)

        # align
        def align_it(start, strong):
            water = self.water_z
            #map3d = self.copy()
            size = (abs(start)*2) + self.size - strong
            start = start + strong
            coords_map = []
            for x in xrange(start,size):
                for y in xrange(start,size):
                    coords_map.append( (x, y) )

            random.shuffle(coords_map)

            lens = strong * (3.0 ** 2)
            for coord in coords_map:
                average = 0.0
                x, y = coord
                #rounds = self.get_round_xy_land(coord, -strong, False)
                #for r_coord in rounds:
                #average += self[r_coord]
                for x in xrange(-strong, strong+1):
                    for y in xrange(-strong, strong+1):
                        average += self[x, y]

                height = int(round(average / lens))
                #height = int(round(average / float(len(rounds))))
                if self[coord] <= water and height > water:
                    height = water
                elif self[coord] > water and height <= water:
                    height = water + 1

                #print self[coord], '->', height

                self[coord] = height

        if First:
            t = time.time()
            add_heights()
            start = 0
            for x in xrange(1):
                square_diamond(start, start, self.size, 500)
                #align_it(-1, 1)
            print 'First generate: ', time.time()  - t
        else:
            t = time.time()
            #start = self.size / 4
            start = -self.size
            print start, self.size+(abs(start)*2)
            square_diamond(start, start, self.size+(abs(start)*2), 1)
            print 'square: ', time.time()  - t
            t = time.time()
            #smooth_all_coasts()
            print 'smooth: ', time.time() - t
            t = time.time()
            #align_it(start, 1)
            #align_it(1, self.size)
            print 'align heights: ', time.time() - t


def map2d_to_3d(map2d, seed):
    """docstring for map2d_to_3d

    """
    config = Config()
    map3d = Map3d(None, map2d.size, seed, True)
    for coords in map2d:
        # if water
        if map2d[coords] == 0:
            map3d[coords] = map3d.water_z
        else:
            map3d[coords] = map3d.water_z+1

    for x in xrange(config.factor):
        for y in xrange(config.factor):
            map3d.land_seeds[x, y] = random.randint(0, sys.maxint)

    map3d.gen_random_heights(True)
    return map3d


def generate_heights(map_tree, source_map, start_x, start_y, DontGen = False, DictMap = {}):
    """
    docstring for generate_heights
    """
    config = Config()
    #import pdb; pdb.set_trace()
    seed = source_map.land_seeds[start_x, start_y]
    map3d = Map3d(map_tree, source_map.size, seed, False)
    map3d.map_x = start_x
    map3d.map_y = start_y
    for x in xrange(map3d.size):
        for y in xrange(map3d.size):
            sx = (x / config.factor) + (start_x * config.factor)
            sy = (y / config.factor) + (start_y * config.factor)
            # heights
            if DontGen and (x, y) in DictMap:
                height = DictMap[(x, y)]
            else:
                height = source_map[(sx, sy)]
            map3d[(x, y)] = height

    if not DontGen:
        map3d.gen_random_heights(False)
    return map3d

#def create_map_3d(map_tree, source_map, start_x, start_y):
    #"""
    #docstring for generate_heights
    #"""
    #config = Config()
    ##import pdb; pdb.set_trace()
    #seed = source_map.land_seeds[start_x, start_y]
    #map3d = Map3d(map_tree, source_map.size, seed, False)
    #map3d.map_x = start_x
    #map3d.map_y = start_y
    #for x in xrange(map3d.size):
        #for y in xrange(map3d.size):
            #sx = (x / config.factor) + (start_x * config.factor)
            #sy = (y / config.factor) + (start_y * config.factor)
            ## heights
            #height = source_map[(sx, sy)]
            #map3d[(x, y)] = height

    #map3d.gen_random_heights(False)
    #return map3d

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

