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

class World():
    """
    docstring for World
    """
    map_2d = None
    #map_3d = None
    maps = None
    cam_coords = (0, 0, 0)
    map_coords = {16: (128, 128, 0)}
    # chanks {level: {(x, y): Chank}}, where x, y = X*16, Y*16 with cubes
    chanks_map = {}
    size_chank = 16
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

        #self.megacube = CubeModel(16, 16, 128)
        #self.megacube.setTexture(textures['dirt'], 1)
        #self.megacube.reparentTo(render)
        #self.megacube.setPos(0,0,0)

        for i in xrange(1,17):
            self.chanks_map[i] = {}

def show_terrain(game, cam_coords, level):
    #loc.loadTerrain(heightmap)
    #lod = LODNode('suber')
    #lod.addSwitch(100.0, 0)
    #lod_node = NodePath(lod)
    #lod_node.reparentTo(render)

    size_chank = game.world.size_chank

    last_camX, last_camY, last_camZ = game.world.cam_coords
    camX, camY, camZ = cam_coords
    game.world.cam_coords = cam_coords

    OK = False

    OK = game.world.new
    game.world.new = False

    try:
        lastX, lastY, lastZ = game.world.map_coords[level]
    except KeyError:
        lastX, lastY, lastZ = [0, 0, 0]
        OK = True

    X = int(camX) / 256
    X = X * 256
    X = int(camX) - X

    Y = int(camY) / 256
    Y = Y * 256
    Y = int(camY) - Y

    Z = int(camZ)

    if X > 255: X = X - 255
    if Y > 255: Y = Y - 255
    if X <0: X = 255 + X
    if Y <0: Y = 255 + Y

    game.world.map_coords[level] = (X, Y, Z)

    if (lastX, lastY) != (X, Y):
        OK = True

    if not OK:
        return

    last_level = game.world.level
    game.world.level = level
    if not game.world.maps:
        return
    if game.world.maps.has_key(level):
        level_maps = game.world.maps[level]
    else:
        game.world.maps[level] = {}
        level_maps = {}

    if level != last_level:

        for ch in game.world.chanks_map[last_level]:
            game.world.chanks_map[last_level][ch].destroy()

        del game.world.chanks_map[last_level]

        game.world.chank_changed = True
        game.world.level = level
        X, Y, Z = (128, 128, 0)
        lastX, lastY, lastZ = (128, 128, 0)
        game.world.d_coords = 0, 0, 0
        d_X, d_Y, d_Z = game.world.d_coords


    if (X / size_chank, Y / size_chank) != (lastX / size_chank, lastY / size_chank):
        for ch in game.world.chanks_map[last_level].values():
            ch.hide()
        game.world.chank_changed = True


    if not game.world.chank_changed:
        return

    if level == 16:
        cur_map = level_maps[(0, 0)]
    else:
        lvlX, lvlY, lvlZ = game.world.map_coords[level+1]
        lvlX, lvlY = lvlX/size_chank, lvlY/size_chank
        if level_maps.has_key((X / size_chank, Y / size_chank)):
            cur_map = level_maps[(X / size_chank, Y / size_chank)]
        else:
            t = time.time()
            if level+1 == 16:
                gen_heights = Generate_Heights(game.world.maps[level+1][(0, 0)], lvlX, lvlY)
            else:
                gen_heights = Generate_Heights(game.world.maps[level+1][(lvlX, lvlY)], lvlX, lvlY)
            for i in gen_heights.start():
                pass
            cur_map = gen_heights.map3d
            game.world.maps[level][(X / size_chank, Y / size_chank)] = cur_map
            print 'gen', time.time()-t
    types = {}
    t= time.time()

    cube_size = game.world.cube_size
    types = game.world.types

    chanks = 4

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
    #planet.setPos(128,128,380)


#def generate_heights_image(map_world):
    #size = map_world.size
    #image = PNMImage(size+1, size+1)
    #image.fill(0,0,0)
    #for x, y in map_world:
        #val = map_world[(x, y)]
        #image.setPixel(x, y, (val, val, val))
    ## size+, size+1 - get values
    #for x in xrange(size, size+1):
        #for y in xrange(size):
            #val = map_world[(x-1, y)]
            #image.setPixel(x, y, (val, val, val))
    #for y in xrange(size, size+1):
        #for x in xrange(size):
            #val = map_world[(x, y-1)]
            #image.setPixel(x, y, (val, val, val))
    #return image

def generate_map_texture(map_world):
    size = map_world.size
    image = PNMImage(size, size)
    image.fill(0,0,0)
    for x, y in map_world:
        if map_world[(x, y)] == map_world.water_z:
            image.setPixel(x, y, (0, 0, 100))
        else:
            image.setPixel(x, y, (0, 100, 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

