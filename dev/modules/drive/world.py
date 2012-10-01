#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import math
import time

from modules.drive.shapeGenerator import Cube as CubeModel
from panda3d.core import Vec3
from modules.drive.textures import textures
from pandac.PandaModules import Texture, TextureStage
from panda3d.core import VBase3
from config import Config
from pandac.PandaModules import NodePath, PandaNode
from panda3d.core import RigidBodyCombiner, NodePath

class QuadroTreeNode:
    """Node - one cube, which may divide on 4 cubes, when camera is near

    Node = X, Y, where Z - height from perlin noize generator -> perlin(x, y, level)

    X,Y this is one of 64 x 64 global map height

    level - depend of height camera
    """

    # stop value
    stop = False
    # exist = True #make voxel deletable by player
    childs = {}
    def __init__(self, vox, len_cube, parent=None,\
                       level = 1, center = Vec3(0,0,0)):

        #print 'Create node: ', len_cube, level, center
        self.parent = parent
        self.level = level
        self.center = center
        self.world = vox.world
        self.vox = vox
        self.voxmap = vox.voxmap
        self.len_cube = len_cube
        #self.cube = self.vox.cube

    #LOD HERE!
    def divide(self):
        #TODO: add #exist chech
        #TODO: add distance check to make LOD
        # divide if distance from camera to node is lower than trigger value
        #const = 5 distances for example
        trigger_dist = self.len_cube*5
        #print trigger_dist, VBase3.length(self.center - base.camera.getPos())
        #print self.center, base.camera.getPos()
        length = VBase3.length(self.center - self.voxmap.camPos)
        #print length, '<', trigger_dist
        if length < trigger_dist :
            if not self.stop:
                for dC in self.vox.v:
                    name = self.center + dC * (self.len_cube)
                    self.childs[name] = QuadroTreeNode(self.vox, self.len_cube/2.0, self, \
                        self.level+1, name)
                    self.childs[name].repaint()
        else:
            self.stop = True

    def check(self):
        #if dist higher then sphere radius then stop dividind

        #TODO: make perlin noise integration
        #X = self.center[0]
        #Y = self.center[1]
        #Z = self.center[2]

        #convert cube center XYZ coordinates to xy texture coordinates

        #see wiki sphere coordinates
        #x = math.atan(math.sqrt(X ** 2 + Y ** 2) / Z)
        #y = math.atan(Y / X)

        # if VBase3.length(self.center) > r+height_map_value(x,y,self.level):

        #if dist higher then sphere radius then stop dividind
        if self.len_cube == 1.0:
            self.stop = True
            return

        #if VBase3.length(self.center) < self.vox.r + (self.len_cube * 0.5 * math.sqrt(2)):
            #self.stop = False
            #return

        #if VBase3.length(self.center) > self.vox.r - (self.len_cube * 0.5 * math.sqrt(2)):
            #self.stop = True

        #stop at bottom level
    def draw(self):
        #if self.level == 1:
        #print self.center
        #if self.len_cube == 1:
        self.vox.voxels[self.center, self.len_cube] = False
        if self.stop or self.len_cube == 1.0:
            self.vox.voxels[self.center, self.len_cube] = True

    def repaint(self):
        self.stop = False
        self.check()
        self.divide()
        self.draw()



class VoxObject():
    #r = 0.5* max_len * 2 ** 0.5
    #r = 0.25* max_len * (2 ** 0.5)
    #r = 0.25* max_len * (3 ** 0.5)
    v = [
         Vec3(0., 0.5, 0.5), Vec3(0.5, 0., 0.5),
         Vec3(0., 0., 0.5), Vec3(0.5, 0.5, 0.5),
         ]

    config = Config()

    def __init__(self, voxmap, world, center, max_len):

        #self.rigid = RigidBodyCombiner('sphere {0}'.format(random.random()))
        self.center = center

        #self.cube = CubeModel(1, 1, 1)
        #self.cube.setTexture(textures['black'])
        self.max_len = max_len
        self.voxmap = voxmap

        self.world = world

        #self.combiner = NodePath(self.rigid)
        #self.combiner.reparentTo(render)
        self.root = QuadroTreeNode(self, self.max_len, center = self.center)
        self.voxels = {}
        self.cubes = {}

        self.generate()
        self.show()

    def generate(self):
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event
        collect = False
        t = time.time()
        for voxel in self.voxels:
            if self.voxels[voxel]:
                if not self.cubes.has_key(voxel):
                    self.cubes[voxel] = CubeModel(voxel[1], voxel[1], voxel[1])
                    mid_mount_level = self.config.mid_mount_level
                    self.cubes[voxel].setTexture(textures[mid_mount_level])
                    self.cubes[voxel].setPos(voxel[0])
                    self.cubes[voxel].reparentTo(render)
                else:
                    if self.cubes[voxel].isHidden():
                        self.cubes[voxel].show()
            else:
                if self.cubes.has_key(voxel):
                    if not self.cubes[voxel].isHidden():
                        self.cubes[voxel].hide()


        print 'Go voxels: ', time.time() - t
        #if collect:
            #t = time.time()
            ##self.rigid.collect()
            #print 'collect: ', time.time() - t


class VoxMap():
    max_len = 256
    def __init__(self, world, size, level):
        self.world = world
        self.level = level
        self.size = size
        self.voxes = {}
        base.camera.setPos(self.max_len/2, self.max_len/2, self.max_len/16)
        self.camPos = base.camera.getPos()
        self.create()

    def show(self):
        if VBase3.length(self.camPos - base.camera.getPos()) >=5:
            for vox in self.voxes.values():
                self.camPos = base.camera.getPos()
                self.world.game.write('CamPos: {0}'.format(self.camPos))
                t = time.time()
                vox.generate()
                print 'gen: ', time.time() - t
                t = time.time()
                vox.show()
                print 'show: ', time.time() - t

    def create(self):
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = Vec3(x*self.max_len, y*self.max_len, -self.max_len)
                self.voxes[name] = VoxObject(self, self.world, name, self.max_len)


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

        textures['black'] = loader.loadTexture("res/textures/black.png")
        textures['black'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['black'].setMinfilter(Texture.FTLinearMipmapLinear)

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

        self.vox_map = VoxMap(self, 0, 1)

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
        self.vox_map.show()

# vi: ft=python:tw=0:ts=4

