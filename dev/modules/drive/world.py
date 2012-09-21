#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""

import sys, random
from pandac.PandaModules import GeoMipTerrain,Filename, BitMask32
from pandac.PandaModules import Texture,TextureStage
from pandac.PandaModules import AmbientLight, PointLight

from pandac.PandaModules import Vec4
from pandac.PandaModules import Texture, PNMImage
from modules.drive.landplane import CubesView

class World():
    """
    docstring for World
    """
    map_2d = None
    map_3d = None
    def __init__(self):
        #self.location = gameLocation()
        #self.location.setTexture('res/textures/dirt.png',1,1)
        #self.location.setLights(Vec4(0.6,0.6,0.6,1), Vec4(1,1,1,1))
        #self.planet = LandNode(0,0,256,256, 0)

        self.seed = random.randint(0, sys.maxint)

def show_terrain(map3d):
    #loc.loadTerrain(heightmap)
    types = {}
    types['land'] = loader.loadModel("box")
    types['land'].setTexture(loader.loadTexture("res/textures/dirt.png"),1)
    types['water'] = loader.loadModel("box")
    types['water'].setTexture(loader.loadTexture("res/textures/water.png"),1)
    cubes = {}
    for x in xrange(128):
        for y in xrange(128):
            if map3d[(x,y)]<=map3d.water_z:
                cubes[(x,y,map3d[x,y])] = 'water'
            else:
                cubes[(x,y,map3d[x,y])] = 'land'
    ch = CubesView('all', types, cubes)
    ch.show()
    #planet.setPos(128,128,380)


def generate_heights_image(map_world):
    size = map_world.size
    image = PNMImage(size+1, size+1)
    image.fill(0,0,0)
    for x, y in map_world:
        val = map_world[(x, y)]
        image.setPixel(x, y, (val, val, val))
    # size+, size+1 - get values
    for x in xrange(size, size+1):
        for y in xrange(size):
            val = map_world[(x-1, y)]
            image.setPixel(x, y, (val, val, val))
    for y in xrange(size, size+1):
        for x in xrange(size):
            val = map_world[(x, y-1)]
            image.setPixel(x, y, (val, val, val))
    return image

def generate_map_texture(map_world):
    size = map_world.size
    image = PNMImage(size, size)
    image.fill(0,0,0)
    for x, y in map_world:
        if map_world[(x, y)] <= map_world.water_z:
            image.setPixel(x, y, (0, 0, 255-map_world[(x, y)]))
        else:
            image.setPixel(x, y, (0, 255-map_world[(x, y)], 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

