#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3D map with perlin, diamond-square and other algorithms

Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
"""

import math
import random
import sys
import time

from pandac.PandaModules import PerlinNoise2
from pandac.PandaModules import Texture, PNMImage

class TileMap(dict):
    """Mini map for generate of heights and square-diamond

    config - voxplanet.config
    map2d - voxplanet.map2d.MapDict2D()
    """
    def __init__(self, config, map2d):
        self.size = map2d.size
        self.map2d = map2d
        self.config = config

    def __getitem__(self, item):
        """Overload getitem for toroid
        """
        if self.has_key(item):
            return dict.__getitem__(self, item)
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
            h = self.map2d[x, y]
            self[x, y] = h
            return h

    def generate_pre_heights(self):
        """Generate global template heights
        """

        config = self.config

        def get_lands_oceans():
            oceans, lands = [], []
            for x in xrange(self.size):
                for y in xrange(self.size):
                    coord = x, y
                    if self[coord] <= 0:
                        oceans.append(coord)
                    else:
                        lands.append(coord)
            return lands, oceans

        def add_heights():
            """Add pre heights for diamond-square
            """
            fac_min = 50
            fac_max = 40

            print 'Get lands and oceans'
            t = time.time()
            lands, oceans  = get_lands_oceans()
            print 'lands and oceans getted: ', time.time() - t

            # TODO: create one def with params: mount_level and other for create heights
            # add default heights
            for coord in lands:
                self[coord] = self.config.land_mount_level[1]

            for coord in oceans:
                self[coord] = -self.config.mid_mount_level[1]

            # add low heights for lands
            count_land = int(round(len(lands) * config.factor_low_mount / 100.))
            land_coords = []

            starts = random.randint(count_land / fac_min, count_land / fac_max)
            for start in xrange(starts):
                start_coord = lands[random.randint(0, len(lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.low_mount_level[0], self.config.low_mount_level[1])

            while count_land > 0:
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


            target_lands = land_coords

            # -------------------------------------------------------------------------------
            # add mid heights for lands
            count_land = int(round(len(target_lands) * (config.factor_mid_mount / 100.)))
            land_coords = []

            starts = random.randint(count_land / (fac_min * 3), count_land / (fac_max*3))
            for start in xrange(starts):
                start_coord = target_lands[random.randint(0, len(target_lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.mid_mount_level[0],
                                                   self.config.mid_mount_level[1])

            while count_land > 0:
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


            target_lands = land_coords


            # -------------------------------------------------------------------------------
            # add high heights for lands
            count_land = int(round(len(target_lands) * (config.factor_high_mount / 100.)))
            land_coords = []

            starts = random.randint(count_land / (fac_min * 4), count_land / (fac_max * 3))
            for start in xrange(starts):
                start_coord = target_lands[random.randint(0, len(target_lands)-1)]
                land_coords.append(start_coord)
                self[start_coord] = random.randint(self.config.high_mount_level[0],
                                                   self.config.high_mount_level[1])

            while count_land > 0:
                # for lands
                if count_land > 0:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    try:
                        coord = land_coords[random.randint(0, len(land_coords) - 1)]
                    except ValueError:
                        coord = lands[random.randint(0, len(lands) - 1)]
                    coord = coord[0] + dx, coord[1] + dy
                    #if coord not in land_coords:
                    self[coord] = random.randint(self.config.high_mount_level[0],
                                                 self.config.high_mount_level[1])
                    land_coords.append(coord)
                    count_land -= 1




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
                        add_z = -5
                else:
                    if add_z <= 0:
                        add_z = 5
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
            """Deprecated
            """
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

        if self.config.add_pre_heights:
            print 'Add heights start'
            add_heights()
        print 'Diamond-Square start'
        for x in xrange(1):
            square_diamond(
                        sx = 0,
                        sy = 0,
                        size = self.size, strong=100)


class Map3d(dict):
    """Class for map with heights

    config - voxplanet.config.Config()
    map2d - voxplanet.map2d.MapDict2D
    seed - seed for map

    Dict:
    Keys: (X, Y)
    Values = Heights
    """
    # World size 2 ** 24, in meters
    perlin = {}
    def __init__(self, config, map2d, seed, *args, **params):
        self.config = config
        print 'create tilemap'
        t = time.time()
        self.global_template = TileMap(config, map2d)
        print 'tilemap was created: ', time.time() - t
        self.seed = seed
        self.world_size = self.config.size_world
        self.mod = self.world_size / map2d.size
        random.seed(seed)
        # generate 2 octaves for lands
        print 'Generate octaves: '
        t = time.time()
        mod = self.config.size_mod / 2
        mod += mod / 2
        count_octaves = mod / 2
        count_octaves += count_octaves / 4
        for level in xrange(count_octaves):
            seed = random.randint(0, sys.maxint)
            self.perlin[level] = (PerlinNoise2(sx = self.world_size, sy = self.world_size,
                                       table_size = 256, seed = seed))
            mod -= 1
            ds = 2 ** mod
            self.perlin[level].setScale(ds)

        self.river_perlin = PerlinNoise2(sx = self.world_size, sy = self.world_size,
                                       table_size = 256, seed = seed)
        self.river_perlin.setScale(2 ** (self.config.size_mod-4))
        self.river_perlin_height = PerlinNoise2(sx = self.world_size, sy = self.world_size,
                                       table_size = 256, seed = seed)
        self.river_perlin_height.setScale(2 ** (self.config.size_mod-20))

        t = time.time()
        random.seed(seed)
        self.global_template.generate_pre_heights()
        print 'generated pre heights: ', time.time() - t
        #self.river_map = RiverMap(self, self.config.rivermap_size)
        #self.river_mod = self.world_size / self.config.rivermap_size

    def cosine_interpolate(self, a, b, x):
        """Cosine interpolate for scale minimap
        """
        ft = x * 3.1415927
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + (b * f)

    def template_height(self, x, y):
        """Interpolate minimap scale for perlin (first octave)
        """

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

        return self.cosine_interpolate(E, F, dy)
        #if G == 0:
            #return 0
        #if G > 0:
            #G = G ** (1/2.)
        #else:
            #G = -(abs(G) ** (1/2.))

        #G = int(round(G

        #return G



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
                if height > level+1 or height < -level-1:
                    dh = (p * height) / (level+1)
                else:
                    if 1 > height > 0:
                        height = 1
                    elif 0 >= height > -1:
                        height = -1
                    dh = p * height
                height += dh

            # rivers
            if height > -4.:
                r = self.river_perlin(x, y)
                if r >= 0.1 and r <= 0.101:
                    height = -10. + (self.river_perlin_height(x, y) * 10.)

            self[item] = int(height)
            return int(height)

    def get_map_3d_tex(self, size, filename = None):
        """Generate texture of map
        """
        mod = self.world_size / size
        image = PNMImage(size, size)
        for x in xrange(size):
            for y in xrange(size):
                px = x * mod
                py = y * mod
                height = self[px, py]
                if height <= 0:
                    color = (abs(height) / 50) + 50
                    if color > 255:
                        color = 255
                    image.setPixel(x, y, (0, 0, 255-color))
                else:
                    if height <= self.config.low_mount_level[1]:
                        color = height / 20
                        r = 0
                        g = 50+color
                        b = 0
                        image.setPixel(x, y, (r, g, b))
                    elif height > self.config.low_mount_level[1]:
                        color = height / 50
                        r = color
                        g = color
                        b = color
                        if r > 255:
                            r = 255
                        if g > 255:
                            r = 255
                        if b > 255:
                            b = 255
                        image.setPixel(x, y, (r, g, b))

        if filename != None:
            image.write(filename)

        #for x in xrange(-1, 2):
            #for y in xrange(-1, 2):
               #image.setPixel(int(world.chunks_map.charX)+x, int(world.chunks_map.charY)+y, (255, 0, 0))

        texture = Texture()
        texture.load(image)
        return texture

    def get_heightmap_tex(self, size, filename = None):
        """Generate texture of map
        """
        mod = self.world_size / size
        image = PNMImage(size, size)
        for x in xrange(size):
            for y in xrange(size):
                px = x * mod
                py = y * mod
                height = self[px, py]
                color = height / 50
                r = 0
                g = 0
                b = 0
                if color > 255:
                    color = 255
                if color < 0:
                    color = abs(color)
                    b = color
                else:
                    g = color
                image.setPixel(x, y, (r, g, b))

        if filename != None:
            image.write(filename)

        #for x in xrange(-1, 2):
            #for y in xrange(-1, 2):
               #image.setPixel(int(world.chunks_map.charX)+x, int(world.chunks_map.charY)+y, (255, 0, 0))

        texture = Texture()
        texture.load(image)
        return texture

if __name__ == "__main__":
    import map2d, config
    conf = config.Config()
    gen = map2d.Map_generator_2D(conf, 38745)
    for i, desc in gen.start():
        pass

    print gen.maps.get_ascii(3)
    map2d = gen.end_map

    map3d = Map3d(conf, map2d, 38745)
    map3d.get_map_3d_tex(512, 'map512.png')
    print '512 ok'
    map3d.get_map_3d_tex(1024, 'map1024.png')
    print '1024 ok'
    map3d.get_map_3d_tex(2048, 'map2048.png')
    print '2048 ok'

# vi: ft=python:tw=0:ts=4

