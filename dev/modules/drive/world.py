#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import math
import time

from modules.drive.landplane import LandNode
from modules.drive.shapeGenerator import Cube as CubeModel
from panda3d.core import Vec3
from modules.drive.textures import textures
from pandac.PandaModules import Texture, TextureStage
from panda3d.core import VBase3
from config import Config
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage

class WaterNode():
    """Water plane for nya

    """
    def __init__(self, water_z):
        self.water_z = water_z
        self.create(0, 0, (16777216/8, 16777216/8))

    def create(self, x, y, scale):
        self.water = LandNode(self.water_z)
        #textures['water'].setWrapU(Texture.WMRepeat)
        #textures['water'].setWrapV(Texture.WMRepeat)
        ts = TextureStage('ts')
        #ts.setMode(TextureStage.MDecal)
        self.water.landNP.setTransparency(TransparencyAttrib.MAlpha)
        self.water.landNP.setTexture(ts, textures['water'])
        scale_x, scale_y = scale
        self.water.landNP.setTexScale(ts, scale_x, scale_y)

    def show(self):
        self.water.landNP.show()

    def hide(self):
        self.water.landNP.hide()

    def reset(self, x, y):
        #self.Destroy()
        #self.create(x, y)
        self.water.landNP.show()
        try:
            self.water.landNP.setPos(x, y, self.water_z)
        except:
            pass

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
        self.vox = vox
        self.world = vox.world
        self.voxmap = vox.voxmap
        self.len_cube = len_cube
        x = int(center[0])
        y = int(center[1])
        z = int(self.world.map_3d[x, y])
        self.center = Vec3(x, y, z)
        #self.cube = self.vox.cube

    #LOD HERE!
    def divide(self):
        #TODO: add #exist chech
        #TODO: add distance check to make LOD
        # divide if distance from camera to node is lower than trigger value
        #const = 5 distances for example

        # realizm = 64, but video ram - ebanko =(
        # lets const = 8

        factor = 1

        camZ = self.voxmap.camZ - self.voxmap.land_z
        if camZ > 30000:
            trigger_dist = self.len_cube * 8 * factor
        elif camZ > 20000 and camZ <= 30000:
            trigger_dist = self.len_cube * 7 * factor
        elif camZ > 10000 and camZ <= 20000:
            trigger_dist = self.len_cube * 6 * factor
        elif camZ > 5000 and camZ <= 10000:
            trigger_dist = self.len_cube * 5 * factor
        else:
            trigger_dist = self.len_cube * 4 * factor

        length = VBase3.length(self.center - self.voxmap.camPos)

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
        self.vox.voxels[self.center, self.len_cube, self.level] = False
        if self.len_cube == 1.0:
            self.vox.voxels[self.center, self.len_cube, self.level] = True
            return
        if self.stop:
            self.vox.voxels[self.center, self.len_cube, self.level] = True

    def repaint(self):
        self.stop = False
        self.check()
        self.divide()
        self.draw()



class VoxObject():
    v = [
         Vec3(0., 0.5, 0.), Vec3(0.5, 0., 0.),
         Vec3(0., 0., 0.), Vec3(0.5, 0.5, 0.),
         ]

    config = Config()

    def __init__(self, voxmap, world, center, max_len):

        self.center = center

        self.max_len = max_len
        self.voxmap = voxmap

        self.world = world

        self.root = QuadroTreeNode(self, self.max_len, center = self.center)
        self.voxels = {}
        self.cubes = {}

        self.generate()
        self.show()

    def generate(self):
        for voxel in self.voxels:
            self.voxels[voxel] = False
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event
        for voxel in self.voxels:
            if self.voxels[voxel]:
                if not self.cubes.has_key(voxel):
                    self.cubes[voxel] = CubeModel(voxel[1], voxel[1], 10000)
                    mid_mount_level = self.config.mid_mount_level
                    height = int(voxel[0][2])

                    # texturization
                    if height <= 0:
                        self.cubes[voxel].setTexture(textures['sand'])
                    elif height >= self.config.land_mount_level[0] and height <= self.config.land_mount_level[1]:
                        self.cubes[voxel].setTexture(textures[self.config.land_mount_level])
                    elif height >= self.config.low_mount_level[0] and height <= self.config.low_mount_level[1]:
                        self.cubes[voxel].setTexture(textures[self.config.low_mount_level])
                    elif height >= self.config.mid_mount_level[0] and height <= self.config.mid_mount_level[1]:
                        self.cubes[voxel].setTexture(textures[self.config.mid_mount_level])
                    elif height >= self.config.high_mount_level[0]:
                        self.cubes[voxel].setTexture(textures[self.config.high_mount_level])

                    self.cubes[voxel].setPos(voxel[0][0], voxel[0][1], (voxel[0][2]-10000))
                    self.cubes[voxel].reparentTo(render)
                else:
                    self.cubes[voxel].show()
            else:
                if self.cubes.has_key(voxel):
                    self.cubes[voxel].hide()


class VoxMap():
    max_len = 16777216
    def __init__(self, world, size, level):
        self.world = world
        self.level = level
        self.size = size
        self.voxes = {}
        base.camera.setPos(self.max_len/2, self.max_len/2, 2500000)
        self.camPos = base.camera.getPos()
        self.get_coords()
        self.create()

    def get_coords(self):
        self.camX = int(base.camera.getX())
        self.camY = int(base.camera.getY())
        self.camZ = int(base.camera.getZ())
        self.land_z = int(self.world.map_3d[self.camX, self.camY])

    def show(self):
        self.get_coords()
        self.far = abs(((self.camZ) / 100)+1)*500
        if self.far < 5000:
            self.far = 5000
        base.camLens.setFar(self.far)
        self.world.game.write('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                              'land height: {3}'.format(self.camX, self.camY, self.camZ,
                               self.land_z))

        if VBase3.length(self.camPos - base.camera.getPos()) >=5:
            for vox in self.voxes.values():
                self.camPos = base.camera.getPos()
                t = time.time()
                vox.generate()
                #print 'gen: ', time.time() - t
                t = time.time()
                vox.show()
                #print 'show: ', time.time() - t

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

        #self.water = WaterNode(1)
        #self.water.show()


    def new(self):
        """New world
        """
        textures['world_map'] = textures.get_map_3d_tex(self, 512)
        textures['world_map'].setWrapU(Texture.WMMirrorOnce)
        textures['world_map'].setWrapV(Texture.WMMirrorOnce)
        ts = TextureStage('world_map_ts')
        self.cubik.setTexture(ts, textures['world_map'])
        self.cubik.setTexScale(ts, 0.5, 0.5)
        self.vox_map = VoxMap(self, 0, 1)

    def show(self):
        self.vox_map.show()
        pass

# vi: ft=python:tw=0:ts=4

