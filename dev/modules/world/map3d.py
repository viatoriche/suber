#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
3D map with perlin, diamond-square and other algorithms
"""

import sys
import random
import time
import math
from pandac.PandaModules import PerlinNoise2
#from PIL import Image
from config import Config

class TileMap(dict):
    config = Config()
    def __init__(self, size, *args, **params):
        dict.__init__(self, *args, **params)
        self.size = size

    def __getitem__(self, item):
        if self.has_key(item):
            return self.get(item)
        else:
            x, y = item

            if x > self.size - 1:
                x = x - self.size
            if y > self.size - 1:
                y = y - self.size
            if y < 0:
                y = self.size + y
            if x < 0:
                x = self.size + x

            return self.get(x, y)

    def generate_pre_heights(self):
        """Generate global template heights
        """

        config = self.config

        def add_heights():

            fac_min = 50
            fac_max = 40

            def get_lands_oceans():
                oceans, lands = [], []
                for coord in self:
                    if self[coord] <= 0:
                        oceans.append(coord)
                    else:
                        lands.append(coord)
                return lands, oceans


            lands, oceans  = get_lands_oceans()


            # TODO: create one def with params: mount_level and other for create heights
            # add default heights
            for coord in lands:
                self[coord] = random.randint(1, self.config.land_mount_level[1])

            for coord in oceans:
                self[coord] = random.randint(-self.config.land_mount_level[1]*3, 0)

            # add low heights for lands
            count_land = int(round(len(lands) * config.factor_low_mount / 100.))
            count_ocean = int(round(len(oceans) * config.factor_low_mount / 100.))
            land_coords = []
            ocean_coords = []

            starts = random.randint(count_land / fac_min, count_land / fac_max)
            for start in xrange(starts):
                start_coord = lands[random.randint(0, len(lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.low_mount_level[0], self.config.low_mount_level[1])

            starts = random.randint(count_ocean / fac_min, count_ocean / fac_max)
            for start in xrange(starts):
                start_coord = oceans[random.randint(0, len(oceans)-1)]
                ocean_coords.append(start_coord)
                self[start_coord] = random.randint(-self.config.low_mount_level[1], -self.config.low_mount_level[0])

            while count_land > 0 and count_ocean > 0:
                # for lands
                if count_land > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = land_coords[random.randint(0, len(land_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    if coord not in land_coords:
                        self[coord] = random.randint(self.config.low_mount_level[0], self.config.low_mount_level[1])
                        land_coords.append(coord)
                        count_land -= 1

                # for oceans
                if count_ocean > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = ocean_coords[random.randint(0, len(ocean_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    if coord not in ocean_coords:
                        self[coord] = random.randint(-self.config.low_mount_level[1], -self.config.low_mount_level[0])
                        ocean_coords.append(coord)
                        count_ocean -= 1


            target_lands = land_coords
            target_oceans = ocean_coords

            # -------------------------------------------------------------------------------
            # add mid heights for lands
            count_land = int(round(len(target_lands) * (config.factor_mid_mount / 100.)))
            count_ocean = int(round(len(target_oceans) * (config.factor_mid_mount / 100.)))
            land_coords = []
            ocean_coords = []

            starts = random.randint(count_land / (fac_min * 3), count_land / (fac_max*3))
            for start in xrange(starts):
                start_coord = target_lands[random.randint(0, len(target_lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.mid_mount_level[0],
                                                   self.config.mid_mount_level[1])

            starts = random.randint(count_ocean / (fac_min * 3), count_ocean / (fac_max * 3))
            for start in xrange(starts):
                start_coord = target_oceans[random.randint(0, len(target_oceans)-1)]
                ocean_coords.append(start_coord)
                self[start_coord] = random.randint(-self.config.mid_mount_level[1],
                                                   -self.config.mid_mount_level[0])

            while count_land > 0 and count_ocean > 0:
                # for lands
                if count_land > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = land_coords[random.randint(0, len(land_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    #if coord not in land_coords:
                    self[coord] = random.randint(self.config.mid_mount_level[0],
                                                 self.config.mid_mount_level[1])
                    land_coords.append(coord)
                    count_land -= 1

                # for oceans
                if count_ocean > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = ocean_coords[random.randint(0, len(ocean_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    #if coord not in ocean_coords:
                    self[coord] = random.randint(-self.config.mid_mount_level[1],
                                                 -self.config.mid_mount_level[0])
                    ocean_coords.append(coord)
                    count_ocean -= 1


            target_lands = land_coords
            target_oceans = ocean_coords


            # -------------------------------------------------------------------------------
            # add high heights for lands
            count_land = int(round(len(target_lands) * (config.factor_high_mount / 100.)))
            count_ocean = int(round(len(target_oceans) * (config.factor_high_mount / 100.)))
            land_coords = []
            ocean_coords = []

            starts = random.randint(count_land / (fac_min * 4), count_land / (fac_max * 3))
            for start in xrange(starts):
                start_coord = target_lands[random.randint(0, len(target_lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.high_mount_level[0],
                                                   self.config.high_mount_level[1])

            starts = random.randint(count_ocean / (fac_min * 4), count_ocean / (fac_max * 4))
            for start in xrange(starts):
                start_coord = target_oceans[random.randint(0, len(target_oceans)-1)]
                ocean_coords.append(start_coord)
                self[start_coord] = random.randint(-self.config.high_mount_level[1],
                                                   -self.config.high_mount_level[0])

            while count_land > 0 and count_ocean > 0:
                # for lands
                if count_land > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = land_coords[random.randint(0, len(land_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    #if coord not in land_coords:
                    self[coord] = random.randint(self.config.high_mount_level[0],
                                                 self.config.high_mount_level[1])
                    land_coords.append(coord)
                    count_land -= 1

                # for oceans
                if count_ocean > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    coord = ocean_coords[random.randint(0, len(ocean_coords) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    #if coord not in ocean_coords:
                    self[coord] = random.randint(-self.config.high_mount_level[1],
                                                 -self.config.high_mount_level[0])
                    ocean_coords.append(coord)
                    count_ocean -= 1


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
                if self[X] <= 0:
                    if add_z > 0:
                        add_z = 0
                else:
                    if add_z <= 0:
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
            water = 0
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

        add_heights()
        for x in xrange(1):
            square_diamond(
                        sx = 0,
                        sy = 0,
                        size = self.size, strong=200)


class Map3d(dict):
    """Class for map with heights

       Keys: (X, Y)
       Values = Heights
    """
    # World size 2 ** 24, in meters
    config = Config()
    perlin = {}
    def __init__(self, map2d, seed, size, *args, **params):
        dict.__init__(self, *args, **params)
        self.global_template = TileMap(map2d.size, map2d.copy())
        self.seed = seed
        self.world_size = self.config.size_world
        self.mod = self.world_size / map2d.size
        random.seed(seed)
        # generate 2 octaves for lands
        for level in xrange(12):
            seed = random.randint(0, sys.maxint)
            self.perlin[level] = (PerlinNoise2(sx = self.world_size, sy = self.world_size,
                                       table_size = self.world_size, seed = seed))
            self.perlin[level].setScale((2 ** (self.config.size_mod-3)) / (2 ** level))

        print 'generate_pre_heights: '
        t = time.time()
        self.global_template.generate_pre_heights()
        print 'generated pre heights! ', time.time() - t

    def cosine_interpolate(self, a, b, x):
        ft = x * 3.1415927
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + (b * f)

    def template_height(self, x, y):

        tx = float(x) / self.world_size
        tx = tx * self.global_template.size

        ty = float(y) / self.world_size
        ty = ty * self.global_template.size

        tx1 = int(tx)
        dx = tx - tx1
        tx2 = tx1 + 1

        ty1 = int(ty)
        dy = ty - ty1
        ty2 = ty1 + 1

        if tx2 > self.global_template.size-1:
            tx2 = tx1
        if ty2 > self.global_template.size-1:
            ty2 = ty1

        A = self.global_template[tx1, ty1]
        B = self.global_template[tx2, ty1]
        C = self.global_template[tx1, ty2]
        D = self.global_template[tx2, ty2]

        E = self.cosine_interpolate(A, B, dx)
        F = self.cosine_interpolate(C, D, dx)

        G = self.cosine_interpolate(E, F, dy)
        #if G == 0:
            #return 0
        #if G > 0:
            #G = G ** (1/2.)
        #else:
            #G = -(abs(G) ** (1/2.))

        G = int(round(G))

        return G

        #print tx1, tx2, dx, self.cosine_interpolate(tx1, tx2, dx)


    def create_image(self, x, y, size, level, filename):
        """Generate image with heights
        """
        #image1 = Image.new("RGB", (size, size), (0, 0, 0, 0))
        #for x in xrange(x, size):
            #for y in xrange(y, size):
        pass

    def __getitem__(self, item):
        """If item not in dict, when perlin generate and return
        """
        # TODO: add cache to hard
        if item in self:
            return dict.__getitem__(self, item)
        else:
            # generate perlin height
            x, y = item
            if x < 0:
                x = x + self.world_size
            if y < 0:
                y = y + self.world_size

            if x >= self.world_size:
                x = x - self.world_size
            if y >= self.world_size:
                y = y - self.world_size

            height = self.template_height(x, y)

            for level in self.perlin:
                p = self.perlin[level](x, y)
                height += p * height

            return height

if __name__ == "__main__":
    maps = __import__('map2d')
    gen = maps.Map_generator_2D(iters = 3)
    for i, desc in gen.start():
        pass

    print gen.maps.get_ascii(i)
    map2d = gen.end_map


# vi: ft=python:tw=0:ts=4

