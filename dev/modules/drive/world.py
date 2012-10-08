#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import math
import time

from modules.drive.landplane import LandNode, ChunkModel
from modules.drive.shapeGenerator import Cube as CubeModel
from panda3d.core import Vec3, Vec2
from modules.drive.textures import textures
from panda3d.core import NodePath
from pandac.PandaModules import Texture, TextureStage
from panda3d.core import VBase3
from config import Config
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from modules.drive.support import ThreadPandaDo
import sys

#sys.setrecursionlimit(65535)

class WaterNode():
    """Water plane for nya

    """
    config = Config()
    def __init__(self, water_z):
        self.water_z = water_z
        self.create(0, 0, (self.config.size_region/2, self.config.size_region/2))

    def create(self, x, y, scale):
        self.water = LandNode(self.water_z, self.config.size_region)
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
    # exist = True #make voxel deletable by player
    def __init__(self, chunks_clt, len_chunk, parent=None,\
                       level = 1, center = (0,0,0)):

        self.parent = parent
        self.level = level
        self.chunks_clt = chunks_clt
        self.world = chunks_clt.world
        self.chunks_map = chunks_clt.chunks_map
        self.len_chunk = len_chunk
        self.childs = {}
        x = center[0]
        y = center[1]
        z = self.world.map_3d[x, y]
        self.center = x, y, z
        self.hide()

    def repaint(self):
        if self.len_chunk > self.chunks_map.chunk_len:
            divide_dist = self.len_chunk
            show_dist = self.chunks_map.far
            #print 'Center and char: ', self.center, self.chunks_map.charX, self.chunks_map.charY, self.chunks_map.camZ
            length_cam = VBase3.length(Vec3(self.center) - Vec3(self.chunks_map.charX,
                                                                self.chunks_map.charY,
                                                                self.chunks_map.camZ))
            if length_cam < divide_dist:
                self.divide()
            elif length_cam < show_dist:
                self.show()
        else:
            self.show()

    def divide(self):
        #print '\t\t\t xxx START DIVIDE: ', self.center
        if self.childs == {}:
            new_len = self.len_chunk/2
            new_center = self.len_chunk/4
            #name = self.center + dC * self.len_chunk
            # <- up
            name = self.center[0] - new_center, self.center[1] - new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                    self.level+1, name)
            self.childs[name].repaint()
            # -> up
            name = self.center[0] + new_center, self.center[1] - new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                    self.level+1, name)
            self.childs[name].repaint()
            # <- down
            name = self.center[0] - new_center, self.center[1] + new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                    self.level+1, name)
            self.childs[name].repaint()
            # -> down
            name = self.center[0] + new_center, self.center[1] + new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                    self.level+1, name)
            self.childs[name].repaint()
        else:
            for child in self.childs:
                self.childs[child].repaint()

    def show(self):
        self.chunks_clt.chunks[self.center, self.len_chunk, self.level] = True

    def hide(self):
        self.chunks_clt.chunks[self.center, self.len_chunk, self.level] = False

class ChunksCollection():
    #v = [
         #Vec3(0., 0.5, 0.), Vec3(0.5, 0., 0.),
         #Vec3(0., 0., 0.), Vec3(0.5, 0.5, 0.),
         #]

    config = Config()
    chunks = {}
    thread_done = True

    def __init__(self, chunks_map, world, center, size_world):

        self.center = center

        self.size_world = size_world
        self.chunks_map = chunks_map

        self.world = world

        self.root = QuadroTreeNode(self, self.size_world, center = self.center)
        self.chunks_models = {}

        self.generate()
        self.show()

    def generate(self):
        for chunk in self.chunks:
            self.chunks[chunk] = False
        #self.chunks = {}
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event

        for chunk_model in self.chunks_models:
            if not self.chunks[chunk_model]:
                length_cam = VBase3.length(Vec3(chunk_model[0]) - Vec3(self.chunks_map.charX,
                                                                       self.chunks_map.charY,
                                                                       self.chunks_map.camZ))
                detach_dist = self.chunks_map.far * 4
                attach_dist = self.chunks_map.far * 2

                if length_cam >= detach_dist:
                    #print 'detach: ', chunk_model
                    if self.chunks_models[chunk_model].hasParent():
                        self.chunks_models[chunk_model].detachNode()
                if length_cam <= attach_dist:
                    #print 'attach: ', chunk_model
                    if not self.chunks_models[chunk_model].hasParent():
                        self.chunks_models[chunk_model].reparentTo(self.world.root_node)

                if not self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].hide()
            else:
                if self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].show()
                self.chunks_models[chunk_model].setX(self.chunks_map.DX)
                self.chunks_models[chunk_model].setY(self.chunks_map.DY)

        for chunk in self.chunks:
            if not self.chunks_models.has_key(chunk):
                # size of chunk
                self.chunks_models[chunk] = ChunkModel(self.world,
                                                       chunk[0][0], chunk[0][1], chunk[1],
                                                       self.chunks_map.chunk_len
                                                       )
                self.chunks_models[chunk].reparentTo(self.world.root_node)
                self.chunks_models[chunk].setX(self.chunks_map.DX)
                self.chunks_models[chunk].setY(self.chunks_map.DY)

                #print 'New coords: X: ', chunk[0][0], ' -> ', self.chunks_models[chunk].getX(),\
                                  #'Y: ', chunk[0][1], ' -> ', self.chunks_models[chunk].getY(), ' len: ', chunk[1]

                if not self.chunks[chunk]:
                    self.chunks_models[chunk].hide()

class ChunksMap():
    config = Config()
    def __init__(self, world, size, level):
        self.world = world
        self.level = level
        self.size = size
        self.size_region = self.config.size_region
        self.size_world = self.config.size_world
        self.chunk_len = 4
        self.chunks_clts = {}
        #self.world.root_node.setPos(0, 0, -10000)
        base.camera.setPos(0, 0, 10000)
        #base.camera.setPos(0, 0, 25000000)
        self.camPos = base.camera.getPos(self.world.root_node)
        base.camLens.setFar(100000)
        self.charX = 0
        self.charY = 0
        self.camX = 0
        self.camY = 0
        self.DX = 0
        self.DY = 0
        self.get_coords()
        self.create()

    def get_coords(self):
        d_charX = int(base.camera.getX(self.world.root_node)) - self.camX
        d_charY = int(base.camera.getY(self.world.root_node)) - self.camY
        self.camX = int(base.camera.getX(self.world.root_node))
        self.camY = int(base.camera.getY(self.world.root_node))
        self.camZ = int(base.camera.getZ(self.world.root_node))
        self.land_z = int(self.world.map_3d[self.camX, self.camY])
        #if self.camZ > self.size_region:
            #self.camZ = self.size_region
        #if self.camZ < -self.size_region:
            #self.camZ = -self.size_region
        self.far = self.camZ*10
        self.charX += d_charX
        self.charY += d_charY
        if self.far < 1000:
            self.far = 1000
        base.camLens.setFar(self.far*2)
        if self.camX < 0:
            self.camX = self.camX + self.size_region
        if self.camY < 0:
            self.camY = self.camY + self.size_region
        if self.camX >= self.size_region:
            self.camX = self.camX - self.size_region
        if self.camY >= self.size_region:
            self.camY = self.camY - self.size_region

        if self.charX < 0:
            self.charX = 0
            self.camX = 0
        if self.charY < 0:
            self.charY = 0
            self.camY = 0
        if self.charX >= self.size_world:
            self.charX = self.size_world - 1
            self.camX = self.size_region - 1
        if self.charY >= self.size_world:
            self.charY = self.size_world - 1
            self.camY = self.size_region - 1

        self.DX = (self.charX / self.size_region) * self.size_region
        self.DY = (self.charY / self.size_region) * self.size_region

        base.camera.setPos(self.camX, self.camY, self.camZ)
        self.camPos = base.camera.getPos(self.world.root_node)

    def set_char_coord(self, coord):
        """Set char/cam coords

        coord - X, Y, Z
        """
        x, y, z = coord
        self.charX = x
        self.charY = y

        if self.charX < 0:
            self.charX = 0
            self.camX = 0
        if self.charY < 0:
            self.charY = 0
            self.camY = 0
        if self.charX >= self.size_world:
            self.charX = self.size_world - 1
            self.camX = self.size_region - 1
        if self.charY >= self.size_world:
            self.charY = self.size_world - 1
            self.camY = self.size_region - 1

        self.camX = self.charX - ((self.charX / self.size_region) * self.size_region)
        self.camY = self.charY - ((self.charY / self.size_region) * self.size_region)
        self.camZ = z
        #if self.camZ > self.size_region:
            #self.camZ = self.size_region
        #if self.camZ < -self.size_region:
            #self.camZ = -self.size_region

    def show(self):
        if self.camPos != base.camera.getPos(self.world.root_node):
            self.get_coords()
            self.world.game.write('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                              'land height: {3} | Char: X: {4}, Y: {5}'.format(self.camX, self.camY, self.camZ,
                               self.land_z, self.charX, self.charY))

            for chunks_clt in self.chunks_clts.values():
                #t = time.time()
                chunks_clt.generate()
                #print 'Chunks generate: ', time.time() - t
                #t = time.time()
                chunks_clt.show()
                #print 'Chunks show: ', time.time() - t

    def create(self):
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = (x*self.size_world)+(self.size_world / 2), (y*self.size_world) + (self.size_world / 2), 0
                self.chunks_clts[name] = ChunksCollection(self, self.world, name, self.size_world)


class World():
    config = Config()
    def __init__(self, gui, game):
        self.level = self.config.root_level
        self.seed = random.randint(0, sys.maxint)
        self.game = game
        self.gui = gui
        self.loader = self.gui.app.loader
        loader = self.loader
        self.root_node = NodePath('ROOT')
        self.root_node.reparentTo(render)

        textures['water'] = loader.loadTexture("res/textures/water.png")
        textures['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['black'] = loader.loadTexture("res/textures/black.png")
        textures['black'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['black'].setMinfilter(Texture.FTLinearMipmapLinear)

        #self.water = WaterNode(1)
        #self.water.show()


    def new(self):
        """New world
        """
        textures['world_map'] = textures.get_map_3d_tex(self, 512)
        textures['world_map'].setWrapU(Texture.WMMirrorOnce)
        textures['world_map'].setWrapV(Texture.WMMirrorOnce)
        ts = TextureStage('world_map_ts')
        #self.cubik.setTexture(ts, textures['world_map'])
        #self.cubik.setTexScale(ts, 0.5, 0.5)
        self.chunks_map = ChunksMap(self, 0, 1)
        taskMgr.add(self.show, 'WorldShow', priority = 1)

    def show(self, task):
        """Task for showing of world
        """
        self.chunks_map.show()
        return task.cont

# vi: ft=python:tw=0:ts=4

