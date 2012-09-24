#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""

import sys, random
import time
from pandac.PandaModules import Filename, BitMask32
from pandac.PandaModules import AmbientLight, PointLight, LODNode, NodePath

from pandac.PandaModules import Vec4
from pandac.PandaModules import Texture, PNMImage
from modules.drive.landplane import Chank, LandNode
from modules.drive.shapeGenerator import Cube as CubeModel
from modules.world.map3d import Generate_Heights
from modules.drive.textures import textures
from modules.drive.support import ThreadPandaDo


class MapTree():
    # map_tree
    map3d = None
    coords = (0, 0, 64)
    def __init__(self, parent = None):
        # map_tree
        self.parent = parent
        if self.parent:
            x, y, z = self.parent.coords
            self.start_x = x / 16
            self.start_y = y / 16
            # x - (start_x * 16) == cur_x / 16
            # →
            # x == (cur_x / 16) + (start_x * 16)
            cur_x = (x - (self.start_x * 16)) * 16
            cur_y = (y - (self.start_y * 16)) * 16
            self.coords = (cur_x, cur_y, 64)
            gh = Generate_Heights(self.parent.map3d, self.start_x, self.start_y)
            for i in gh.start(): pass
            self.map3d = gh.map3d

    def down(self):
        return MapTree(self)

    def change_parent_coords(self):
        if self.parent:
            cur_x, cur_y, cur_z = self.coords
            x = (cur_x / 16) + (self.start_x * 16)
            y = (cur_y / 16) + (self.start_y * 16)
            self.parent.coords = (x, y, 64)

    # return True, if join
    # TODO: create
    def join_to_next_land(self):
        pass

    def get_coords_txt(self, level):
        cur_x, cur_y, cur_z = self.coords
        if self.parent:
            par_x, par_y, par_z = self.parent.coords
            return 'L:{8} * X: {0}, Y: {1} -> {2}:{3} * UX: {4}, UY: {5} -> {6}:{7}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, par_x, par_y, par_x/16, par_y/16, level)
        else:
            return 'L:{4} * X: {0}, Y: {1} -> {2}:{3}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, level)


    #def up

class World():
    """
    docstring for World
    """
    map_2d = None
    # kawaii tech for LoD of World, logic Tree based
    map_tree = None
    # chanks {level: {(x, y): Chank}}, where x, y = X*16, Y*16 with cubes
    chanks_map = {}
    size_chank = 16
    # modelles with texture for cubes
    types = {}
    def __init__(self):
        self.seed = random.randint(0, sys.maxint)
        self.chank_changed = True
        self.level = 16
        self.new = True
        textures['dirt'] = loader.loadTexture("res/textures/dirt.png")
        textures['dirt'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['dirt'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['water'] = loader.loadTexture("res/textures/water.png")
        textures['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['sand'] = loader.loadTexture("res/textures/sand.png")
        textures['sand'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['sand'].setMinfilter(Texture.FTLinearMipmapLinear)

        self.cube_size = 1
        self.types['land'] = CubeModel(self.cube_size, self.cube_size, self.cube_size)
        self.types['land'].setTexture(textures['dirt'],1)
        self.types['water'] = CubeModel(self.cube_size, self.cube_size, self.cube_size)
        self.types['water'].setTexture(textures['sand'],1)

        self.paint_thread = False

        for i in xrange(1,17):
            self.chanks_map[i] = {}

def show_terrain(game, cam_coords, level):
    if game.world.paint_thread:
        return

    size_chank = game.world.size_chank

    camX, camY, camZ = cam_coords

    OK = False

    OK = game.world.new
    game.world.new = False

    last_level = game.world.level
    game.world.level = level
    if level == last_level:

        lastX, lastY, lastZ = game.world.map_tree.coords

        X = int(camX) / 256
        X = X * 256
        X = int(camX) - X

        Y = int(camY) / 256
        Y = Y * 256
        Y = int(camY) - Y

        Z = int(camZ)

        game.world.map_tree.coords = (X, Y, Z)
        game.write(game.world.map_tree.get_coords_txt(level))
        if X > 255:
            X = X - 255
        if Y > 255:
            Y = Y - 255
        if X <0:
            X = 255 + X
        if Y <0:
            Y = 255 + Y

        game.world.map_tree.coords = (X, Y, Z)
        game.world.map_tree.change_parent_coords()
        game.write(game.world.map_tree.get_coords_txt(level))

        if (lastX, lastY) != (X, Y):
            OK = True

        if not OK:
            return

    else:
        for ch in game.world.chanks_map[last_level]:
            game.world.chanks_map[last_level][ch].destroy()

        game.world.chanks_map[last_level] = {}

        game.world.chank_changed = True

        if level < last_level:
            game.world.map_tree = game.world.map_tree.down()
        if level > last_level:
            if level <17:
                game.world.map_tree = game.world.map_tree.parent

        X, Y, Z = game.world.map_tree.coords
        game.world.map_tree.change_parent_coords()
        game.write(game.world.map_tree.get_coords_txt(level))
        lastX, lastY, lastZ = game.world.map_tree.coords


    cur_map = game.world.map_tree.map3d
    if (X / size_chank, Y / size_chank) != (lastX / size_chank, lastY / size_chank):
        #for ch in game.world.chanks_map[last_level].values():
            #ch.hide()
        game.world.chank_changed = True

    game.cmd_handle('showmap')

    if not game.world.chank_changed:
        return


    def Paint():

        t= time.time()

        cube_size = game.world.cube_size
        types = game.world.types

        chanks = 5

        dx = ((X / size_chank) - chanks) * size_chank
        for xcount in xrange(chanks * 2):
            dy = ((Y / size_chank) - chanks) * size_chank
            for ycount in xrange(chanks * 2):
                chank_X = dx + (256 * (int(camX)/256))
                chank_Y = dy + (256 * (int(camY)/256))
                if game.world.chanks_map[level].has_key((chank_X, chank_Y)):
                    #time_show = time.time()
                    game.world.chanks_map[level][(chank_X, chank_Y)].show()
                    dy += size_chank
                    #print 'time show chank: ', time.time() - time_show
                    continue
                cubes = {}
                time_gen = time.time()
                for x in xrange(dx, dx + size_chank):
                    cX = x
                    if cX < 0:
                        cX = 255+cX
                    if cX > 255:
                        cX = cX-255
                    for y in xrange(dy, dy + size_chank):
                        cY = y
                        if cY < 0:
                            cY = 255+cY
                        if cY > 255:
                            cY = cY-255

                        cube_X = x + (256 * (int(camX)/256))
                        cube_Y = y + (256 * (int(camY)/256))
                        cube_X = cube_X * cube_size
                        cube_Y = cube_Y * cube_size
                        if cur_map[(cX, cY)]<=cur_map.water_z:
                            cubes[(cube_X, cube_Y, cur_map[cX,cY] * cube_size)] = 'water'
                        else:
                            cubes[(cube_X, cube_Y, cur_map[cX,cY] * cube_size)] = 'land'

                #print 'time gen cubes: ', time.time() - time_gen

                #time_create = time.time()
                ch = Chank('ch_{0}_{1}_{2}'.format(level, chank_X, chank_Y), types, game.process.lod_node, game.process.lod)
                ch.new(cubes)
                game.world.chanks_map[level][(chank_X, chank_Y)] = ch

                #print 'time create chank: ', time.time() - time_create
                dy += size_chank
            dx += size_chank

        print 'show', time.time()-t
        game.world.chank_changed = False
        game.world.paint_thread = False


    game.world.paint_thread = True
    Paint()


def generate_map_texture(map_tree, factor):
    map_world = map_tree.map3d
    size = map_world.size / factor
    image = PNMImage(size, size)
    #image.fill(0,0,0)
    for x in xrange(size):
        for y in xrange(size):
            px = x * factor
            py = y * factor
            if map_world[(px, py)] == map_world.water_z:
                image.setPixel(x, y, (0, 0, 100))
            else:
                image.setPixel(x, y, (0, 100, 0))
    char_x, char_y, char_z = map_tree.coords
    char_x = char_x / factor
    char_y = char_y / factor
    if factor>2:
        image.setPixel(char_x, char_y, (255, 0, 0))
    else:
        for x in xrange(char_x - 1, char_x+2):
            cx = x
            if cx > size-1: cx = size-1
            if cx < 0: cx = 0
            for y in xrange(char_y - 1, char_y+2):
                cy = y
                if cy > size-1: cy = size-1
                if cy < 0: cy = 0
                image.setPixel(cx, cy, (255, 0, 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

