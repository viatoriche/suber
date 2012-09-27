#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
2D/3D map generation and classes of maps world
"""

import random
import os
from PIL import Image

class MapDict2D(dict):
    """
    Base class for Map
        Dictionary

        example:
            >>>map = MapDict2D(size = 25, fill = 0)
            >>>map(2,3)
            0
            >>>map.size
            25

    """
    def __init__(self, size, fill = 0):
        """
            size - size of map / size * size square
            fill - fill of map / fill = -1 → don't fill
        """
        dict.__init__(self)

        if fill != -1:
            for x in xrange(size):
                for y in xrange(size):
                    self[x,y] = fill

        self.size = size



class Maps2D(dict):
    """
        Collection dictionary of MapDict2D
            Get map → Maps2D[level],
                where level → detalization of template for map 0,1..N
    """
    def get_ascii(self, level):
        """
        Get pseudo graphic map
            return str
        """
        s = ''
        cmap = self[level]
        for e, x in enumerate(xrange(cmap.size)):
            # for square view delete 1/2 line
            if e % 2 == 0:
                continue
            for y in xrange(cmap.size):
                if cmap[(y, x)] == 0:
                    # water
                    s = s + ' '
                else:
                    # land
                    s = s + '▓'
            s = s + '\n'
        return s

    def align(self, level):
        """
        docstring for align
        """
        coasts = self.get_all_coasts(level, 0)
        cmap = self[level]

        for coords in coasts:
            col = 0
            for round_coords in self.get_round_xy_land(coords, cmap.size):
                col += cmap[round_coords]
            cmap[coords] = int(round(col/9.0))

        coasts = self.get_all_coasts(level, 1)
        cmap = self[level]

        for coords in coasts:
            col = 0
            for round_coords in self.get_round_xy_land(coords, cmap.size):
                col += cmap[round_coords]
            cmap[coords] = int(round(col/9.0))


    def get_all_coasts(self, level, type_land):
        """
        Get coordinates of all coast-point of map
            return list of coordinates:
               [(x1,y1),(x2,y2)...(xN,yN)]
        """
        coasts = []
        cmap = self[level]
        if type_land == 0:
            type_land = 1
        else:
            type_land = 0

        for x,y in cmap:
            # if water - ignore
            if cmap[x,y] == type_land:
                continue
            # get coordinates around this point
            all_round = self.get_round_xy_land((x,y), cmap.size)
            for r_x, r_y in all_round:
                # if there is water around
                if cmap[r_x,r_y] == type_land:
                    # add coordinates to coast list
                    coasts.append((x, y))
                    break
        return coasts

    def create_image(self, filename, level = 0):
        """Create image of map and save to filename
        """
        cmap = self[level]
        size = cmap.size
        image = Image.new("RGB", (size, size), (0,0,0,0))
        for x, y in cmap:
            # water
            if cmap[(x,y)] == 0:
                image.putpixel((x, y), (0, 0, 128))
            # land
            else:
                image.putpixel((x, y), (0, 200, 0))
        image.save(filename, 'PNG')
        del image

    def get_round_xy_land(self, target_coord, size):
        """Get 3x3 square, where target location in center

            target_coord = (targ_x, targ_y) or [targ_x, targ_y]
            size = size of target map

            return:
                list of [(x1, y1)...(x3, y3)]
        """
        targ_x, targ_y = target_coord
        coords = []
        # from -1/-1 to 1/1
        for iter_x in xrange(targ_x-1, targ_x+2):
            round_x = iter_x
            if iter_x == -1:
                round_x = size-1
            if iter_x > size-1:
                round_x = 0
            for iter_y in xrange(targ_y-1, targ_y+2):
                round_y = iter_y
                if iter_y == -1:
                    round_y = size-1
                if iter_y > size-1:
                    round_y = 0

                coords.append((round_x, round_y))

        return coords

class Map_generator_2D():
    """
    Generator of map, without relief, 2D

        Step 1.        | create mini square, random continents etc
        ---------------------------------------------------------
        Step 2...iters | smooth and increase square, by mode
                       | new_size = old_size * mode
        ---------------------------------------------------------
        Step iters     | alias coasts
    """
    params = {}
    def __init__(self, iters = 3, min_land = 25, max_land = 45,
                                    min_continents = 4, max_continents = 6):
        """
        Initialization of generator
        """
        # --> 64
        self.size = 8
        # create dict of MapDict2D
        self.maps = Maps2D()
        # add zero map dict to maps
        self.maps[0] = MapDict2D(self.size, 0)
        self.mode = 2
        self.iters = iters
        self.min_land = min_land
        self.max_land = max_land
        self.min_continents = min_continents
        self.max_continents = max_continents

    def smooth_coasts(self, source_coord, new_coord, iteration, type_land):
        """
        Add water/land for smoothing to coast points for maps[iteration]
            source_coord - source coordinates / pre-iteration map
            new_coord - new coordinates / iteration map

            it is a very impotant function ^__^
        """
        # source_map - pre-iteration map, for get self.mode and send it to
        # get_round_xy_land. For get vectors to water fill.
        # → only from ocean to coast
        source_map = self.maps[iteration-1]
        around = self.maps.get_round_xy_land(source_coord, source_map.size)
        # coordinates list for start of water, borders of squares
        start_waters = []
        source_x, source_y = source_coord
        new_x, new_y = new_coord
        new_size = self.maps[iteration].size
        # middle start point to water
        #middle_mode = int(round(self.mode/2))
        # get start-points for water fill
        for round_x, round_y in around:
            # if water
            if source_map[(round_x, round_y)] == type_land:
                if round_x < source_x:
                    water_x = new_x
                    if round_y < source_y:
                        water_y = new_y
                    else:
                        water_y = new_y + self.mode
                else:
                    water_x = new_x + self.mode
                    if round_y < source_y:
                        water_y = new_y
                    else:
                        water_y = new_y + self.mode
                #if round_x == source_x:
                    #water_x = new_x + middle_mode
                #if round_y == source_y:
                    #water_y = new_y + middle_mode
                #min_x, max_x = new_x, new_x + new_size
                #min_y, max_y = new_y, new_y + new_size
                start_waters.append((water_x, water_y))

        # Filling
        for start_x, start_y in start_waters:
            # Strong of water filling - count of points
            #if random.randint(1, 10 - len(start_waters)) == 1: continue
            strong = random.randint(round((self.mode**2)*0.4),round((self.mode**2)*0.6))


            # Fill land by water
            coord_cont = [(start_x, start_y)]
            # while points of water > 0
            while strong > 0:
                # get random coordinates from land
                target = coord_cont[random.randint(0, len(coord_cont)-1 )]
                # get square 3x3 around target
                square_target = self.maps.get_round_xy_land(target, new_size)
                # get random coordinates from 3x3 for water
                target_coord = square_target[random.randint(0, len(square_target)-1 )]

                #if target_coord < min_xy or target_coord > max_xy:
                    #continue

                # set water to point of land
                self.maps[iteration][target_coord] = type_land
                # save coord for next filling
                coord_cont.append(target_coord)
                # decrease strong of water
                strong -= 1


    def start(self):
        """
        Start generation of world! :3

        Main function

        yield of progress:
            (iter, descripton)
        """
        # generate zero level map
        self.generate_zero()
        # start the iterations of increase and smoothing map
        yield 0, 'zero map created'
        if self.iters == 0:
            return
        for iteration in xrange(1, self.iters + 1):
            yield iteration, 'start iteration'
            size = self.mode

            # coasts for smoothing, other - for increase, fill
            coasts = self.maps.get_all_coasts(iteration-1, 0)
            # get pre-iteration map
            source_map = self.maps[iteration-1]
            # create new maps dict, and no filling
            self.maps[iteration] = MapDict2D(source_map.size * self.mode, -1)
            yield iteration, 'start filling'
            for x, y in source_map:
                # for increasing map get start and end coordinates of square
                start_x = x * size
                end_x = start_x + size
                start_y = y * size
                end_y = start_y + size

                for nx in xrange(start_x, end_x):
                    for ny in xrange(start_y, end_y):
                        self.maps[iteration][(nx, ny)] = source_map[x,y]

            yield iteration, 'filling completed'
            for x, y in coasts:
                # start x, end x
                start_x = x * size
                end_x = start_x + size
                # start y, end y
                start_y = y * size
                end_y = start_y + size
                # ok, add water fill to coasts
                self.smooth_coasts((x, y), (start_x, start_y), iteration, 0)

            coasts = self.maps.get_all_coasts(iteration-1, 1)
            for x, y in coasts:
                # start x, end x
                start_x = x * size
                end_x = start_x + size
                # start y, end y
                start_y = y * size
                end_y = start_y + size
                # ok, add water fill to coasts
                self.smooth_coasts((x, y), (start_x, start_y), iteration, 1)
            yield iteration, 'coasts smoothed'

        yield iteration, 'start align'
        self.maps.align(iteration)
        self.maps.align(iteration)

        yield iteration, 'finish'


    def generate_zero(self):
        """
        Generator of zero map, begin options
        """
        # generate map 0 - ocean, 1 - land
        # number of continents / count of start points
        continents = random.randint(self.min_continents, self.max_continents)
        self.params['continents'] = continents
        # size of land by percents - %
        size_land = random.randint(self.min_land, self.max_land)
        self.params['size_land'] = size_land
        # square of map - math → width * height = all points of map
        all_size = self.size * self.size
        # square of land, real, points
        size_land = round((size_land / 100.0) * all_size)
        # square of ocean, points
        size_ocean = all_size - size_land
        # squares of all continents
        sq_cont = {}
        # for devision land for continents
        about_sq = round(size_land / float(continents))
        min_sq = size_land
        # devision land for continents
        for continent in xrange(1, continents+1):
            sq_cont[continent] = about_sq
            min_sq = min_sq - sq_cont[continent]
        # start generate continents
        for continent in xrange(1, continents + 1):
            xy_ok = False
            # get start coordinates
            while not xy_ok:
                start_x = random.randint(0, self.size-1)
                start_y = random.randint(0, self.size-1)
                # if water - ok
                if self.maps[0][(start_x, start_y)] == 0:
                    self.maps[0][(start_x, start_y)] = 1
                    xy_ok = True

            # for increase continent, decrease free points of continent
            n_land = sq_cont[continent] - 1
            iterations = 0
            max_iter = n_land
            coord_cont = [(start_x,start_y)]
            while n_land > 0:
                # get random target from posible coordinates
                target = coord_cont[random.randint(0, len(coord_cont)-1 )]
                # get square 3x3 around target
                square_target = self.maps.get_round_xy_land(target, self.size)
                # get random point from 3x3
                x,y = square_target[random.randint(0, len(square_target)-1 )]
                # if water then will be land
                if self.maps[0][(x,y)] == 0:
                    self.maps[0][(x,y)] = 1
                    coord_cont.append((x,y))
                    n_land -= 1

        for sea in xrange(random.randint(continents, continents * 2)):
            xy_ok = False
            # get start coordinates
            while not xy_ok:
                start_x = random.randint(0, self.size-1)
                start_y = random.randint(0, self.size-1)
                # if water - ok
                if self.maps[0][(start_x, start_y)] == 1:
                    self.maps[0][(start_x, start_y)] = 0
                    for i in xrange(random.randint(1,6)):
                        square_target = self.maps.get_round_xy_land((start_x, start_y), self.size)
                        x,y = square_target[random.randint(0, len(square_target)-1 )]
                        self.maps[0][(x, y)] = 0
                    xy_ok = True


# Testing ^--^
if __name__ == '__main__':
    iters = 5
    seed = random.randint(1,65535)
    random.seed(seed)
    global_map_gen = Map_generator_2D(iters = iters)
    for i, desc in global_map_gen.start():
        print i, desc
    for i in xrange(global_map_gen.iters+1):
        filename = '/tmp/map{0}.png'.format(i)
        global_map_gen.maps.create_image(filename, i)
        print filename, 'was created!'
    #print global_map_gen.maps.get_ascii(1)
# vi: ts=4 sw=4

