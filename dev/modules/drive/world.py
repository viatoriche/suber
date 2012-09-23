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
    d_coords = (0, 0, 0)
    map_coords = {16: (128, 128, 0)}
    # chanks {level: {(x, y): Chank}}, where x, y = X*16, Y*16 with cubes
    chanks_map = {}
    def __init__(self):
        self.seed = random.randint(0, sys.maxint)
        self.chank_changed = True
        self.level = 16
        self.new = True
        textures['dirt'] = loader.loadTexture("res/textures/dirt.png")
        textures['water'] = loader.loadTexture("res/textures/water.png")
        for i in xrange(1,17):
            self.chanks_map[i] = {}

def show_terrain(game, cam_coords, level, tex):
    #loc.loadTerrain(heightmap)
    #lod = LODNode('suber')
    #lod.addSwitch(100.0, 0)
    #lod_node = NodePath(lod)
    #lod_node.reparentTo(render)

    last_camX, last_camY, last_camZ = game.world.cam_coords
    camX, camY, camZ = cam_coords
    game.world.cam_coords = cam_coords
    d_X, d_Y, d_Z = game.world.d_coords
    game.world.d_coords = d_X - (camX - last_camX), d_Y - (camY - last_camY),\
                          d_Z - (camZ - last_camZ)
    d_X, d_Y, d_Z = game.world.d_coords

    OK = False

    OK = game.world.new
    game.world.new = False

    try:
        lastX, lastY, lastZ = game.world.map_coords[level]
    except KeyError:
        lastX, lastY, lastZ = [0, 0, 0]
        OK = True

    add_X, add_Y, add_Z = d_X, d_Y, d_Z

    if abs(d_X) >= 1:
        add_X = 0
        OK = True
    if abs(d_Y) >= 1:
        add_Y = 0
        OK = True
    if abs(d_Z) >= 1:
        add_Z = 0
        OK = True

    game.world.d_coords = add_X, add_Y, add_Z

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

        for ch in game.world.chanks_map[last_level].values():
            ch.hide()

        game.world.chank_changed = True
        game.world.level = level
        X, Y, Z = (128, 128, 0)
        lastX, lastY, lastZ = (128, 128, 0)
        game.world.d_coords = 0, 0, 0
        d_X, d_Y, d_Z = game.world.d_coords

    else:

        X = lastX + int(d_X)
        Y = lastY + int(d_Y)
        Z = lastZ + int(d_Z)

        if X > 255: X = 0
        if Y > 255: Y = 0
        if X <0: X = 255
        if Y <0: Y = 255

    game.world.map_coords[level] = (X, Y, Z)

    if X/16 != lastX/16 or Y/16 != lastY/16:
        for ch in game.world.chanks_map[last_level].values():
            ch.hide()
        game.world.chank_changed = True


    if not game.world.chank_changed:
        return

    if level == 16:
        cur_map = level_maps[(0, 0)]
    else:
        lvlX, lvlY, lvlZ = game.world.map_coords[level+1]
        if level_maps.has_key((X/16, Y/16)):
            cur_map = level_maps[(X/16, Y/16)]
        else:
            t = time.time()
            if level+1 == 16:
                gen_heights = Generate_Heights(game.world.maps[level+1][(0, 0)], lvlX/16, lvlY/16)
            else:
                gen_heights = Generate_Heights(game.world.maps[level+1][(lvlX/16, lvlY/16)], lvlX/16, lvlY/16)
            for i in gen_heights.start():
                pass
            cur_map = gen_heights.map3d
            game.world.maps[level][(X/16, Y/16)] = cur_map
            print 'gen', time.time()-t
    types = {}
    t= time.time()
    types['land'] = CubeModel(1,1,1)
    types['land'].setTexture(textures['dirt'],1)
    types['water'] = CubeModel(1,1,1)
    types['water'].setTexture(textures['water'],1)
    dx = X-64
    for xcount in xrange(8):
        dy = Y-64
        for ycount in xrange(8):
            if game.world.chanks_map[level].has_key((dx/16, dy/16)):
                game.world.chanks_map[level][(dx/16, dy/16)].show()
                dy += 16
                continue
            cubes = {}
            for x in xrange(dx, dx+16):
                cX = x
                if cX < 0:
                    cX = 255+cX
                if cX > 255:
                    cX = cX-255
                for y in xrange(dy, dy+16):
                    cY = y
                    if cY < 0:
                        cY = 255+cY
                    if cY > 255:
                        cY = cY-255
                    if cur_map[(cX, cY)]<=cur_map.water_z:
                        cubes[(cX,cY,cur_map[cX,cY])] = 'water'
                    else:
                        cubes[(cX,cY,cur_map[cX,cY])] = 'land'

            ch = Chank('ch_{0}_{1}_{2}'.format(level, dx/16, dy/16), types, game.process.lod_node, game.process.lod)
            ch.new(cubes)
            ch.show()
            game.world.chanks_map[level][(dx/16, dy/16)] = ch
            dy += 16
        dx += 16

    base.camera.setX(X)
    base.camera.setY(Y)
    game.world.cam_coords = (X, Y, camZ)

    ch.show()
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

