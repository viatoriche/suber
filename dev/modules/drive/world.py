#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys

from modules.drive.shapeGenerator import Cube as CubeModel
from panda3d.core import Vec3
from modules.drive.textures import textures
from pandac.PandaModules import Texture, TextureStage
from panda3d.core import VBase3
from config import Config

class OctreeNode:

    stop = False
    child = []
    def __init__(self, world, len_cube, parent=None,\
                       level = 1, center = Vec3(0,0,0)):
        self.parent = parent
        self.level = level
        self.center = center
        self.world = world
        self.len_cube = len_cube
        self.cube = self.world.cubik
        #self.v = [Vec3(0,0,-1), Vec3(0,0,1), Vec3(0,-1,0), Vec3(0,1,0), Vec3(-1,0,0), Vec3(1,0,0)]
        self.v = [Vec3(0.5,0.5,0.5), Vec3(-0.5,0.5,0.5), Vec3(0.5,-0.5,0.5), Vec3(0.5,0.5,-0.5), Vec3(-0.5,-0.5,0.5), Vec3(0.5,-0.5,-0.5), Vec3(-0.5,0.5,-0.5), Vec3(-0.5,-0.5,-0.5)]
        #self.r = self.len_cube * 2 ** 0.5

        if self.check():
            self.draw()

    def divide(self):
        if not self.stop:
            for dC in self.v:
                self.child.append(__OctreeNode(self, self.len_cube/2,\
                        self.level+1, self.center + self.dC * length))
                        #self.level+1, self.center + self.dC * length / 2))

    def check(self):
        #if dist higher then sphere radius then stop dividind
        
        #TODO resolve r to right variable
        if VBase3.length(self.center) > r:
            self.stop = True
        #stop at bottom level
        if self.len_cube == 1:
            self.stop = True
        return not self.stop

    def draw(self):
        if self.level == 1:
            #TODO: SHOW CUBE HERE
            self.cube.setScale(self.len_cube/2, self.len_cube/2, self.len_cube/2)
            self.cube.setPos(self.center)

class VoxObject:
    max_len = 256
    r = 0.5* max_len * 2 ** 0.5
    def __init__(self, world):
        self.world = world
        self.root = OctreeNode(self.world, self.max_len)


class World():
    config = Config()
    def __init__(self, gui, game):
        self.level = self.config.root_level
        self.seed = random.randint(0, sys.maxint)
        self.game = game
        self.gui = gui
        self.loader = self.gui.app.loader
        loader = self.loader

        land_mount_level = self.config.land_mount_level
        low_mount_level = self.config.low_mount_level
        mid_mount_level = self.config.mid_mount_level
        high_mount_level = self.config.high_mount_level

        textures[land_mount_level] = loader.loadTexture("res/textures/land.png")
        textures[land_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[land_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[low_mount_level] = loader.loadTexture("res/textures/low_mount.png")
        textures[low_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[low_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[mid_mount_level] = loader.loadTexture("res/textures/mid_mount.png")
        textures[mid_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[mid_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[high_mount_level] = loader.loadTexture("res/textures/high_mount.png")
        textures[high_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[high_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['water'] = loader.loadTexture("res/textures/water.png")
        textures['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['sand'] = loader.loadTexture("res/textures/sand.png")
        textures['sand'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['sand'].setMinfilter(Texture.FTLinearMipmapLinear)

        self.cube_size = self.config.cube_size
        self.cube_z = 1
        self.types = {}

        self.types[land_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[land_mount_level].setTexture(textures[land_mount_level],1)

        self.types[low_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[low_mount_level].setTexture(textures[low_mount_level],1)

        self.types[mid_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[mid_mount_level].setTexture(textures[mid_mount_level],1)

        self.types[high_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[high_mount_level].setTexture(textures[high_mount_level],1)

        self.types['sand'] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types['sand'].setTexture(textures['sand'],1)

        self.cubik = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.cubik.reparentTo(self.gui.app.render)
        self.cubik.setTexture(textures[high_mount_level],1)

        self.vox = VoxObject(self)

    def new(self):
        """New world
        """
        textures['world_map'] = textures.get_map_2d_tex(self.map_2d)
        textures['world_map'].setWrapU(Texture.WMMirrorOnce)
        textures['world_map'].setWrapV(Texture.WMMirrorOnce)
        ts = TextureStage('world_map_ts')
        self.cubik.setTexture(ts, textures['world_map'])
        self.cubik.setTexScale(ts, 0.5, 0.5)

    def show(self):
        pass

# vi: ft=python:tw=0:ts=4

