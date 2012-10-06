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
from panda3d.core import Vec3
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
        self.create(0, 0, (self.config.size_world/8, self.config.size_world/8))

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
            factor = 1
            trigger_dist = self.len_chunk * factor
            trigger_dist2 = self.len_chunk * factor * 3
            length_cam = VBase3.length(Vec3(self.center) - self.chunks_map.camPos)
            if length_cam < trigger_dist:
                self.divide()
            elif length_cam < trigger_dist2:
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

    def __init__(self, chunks_map, world, center, max_len):

        self.center = center

        self.max_len = max_len
        self.chunks_map = chunks_map

        self.world = world

        self.root = QuadroTreeNode(self, self.max_len, center = self.center)
        self.chunks_models = {}

        self.generate()
        self.show()

    def generate(self):
        for chunk in self.chunks:
            self.chunks[chunk] = False
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event

        for chunk_model in self.chunks_models:
            if not self.chunks[chunk_model]:
                if not self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].hide()
            else:
                if self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].show()

        for chunk in self.chunks:
            if not self.chunks_models.has_key(chunk):
                self.chunks_models[chunk] = ChunkModel(self.world,
                                                       chunk[0][0], chunk[0][1], chunk[1], 
                                                       self.chunks_map.chunk_len)
                self.chunks_models[chunk].reparentTo(self.world.root_node)

                if not self.chunks[chunk]:
                    self.chunks_models[chunk].hide()

class ChunksMap():
    config = Config()
    def __init__(self, world, size, level):
        self.world = world
        self.level = level
        self.size = size
        self.max_len = self.config.size_world
        self.chunk_len = 4
        self.chunks_clts = {}
        self.world.root_node.setPos(-self.max_len/2, -self.max_len/2, -2000000)
        base.camera.setPos(0, 0, 0)
        #base.camera.setPos(0, 0, 25000000)
        self.camPos = base.camera.getPos(self.world.root_node)
        self.get_coords()
        self.create()

    def get_coords(self):
        self.camX = int(base.camera.getX(self.world.root_node))
        self.camY = int(base.camera.getY(self.world.root_node))
        self.camZ = int(base.camera.getZ(self.world.root_node))
        self.land_z = int(self.world.map_3d[self.camX, self.camY])
        self.far = self.camZ*5
        if self.far < 2000:
            self.far = 2000
        base.camLens.setFar(self.far)
        self.camPos = base.camera.getPos(self.world.root_node)

    def show(self):
        if self.camPos != base.camera.getPos(self.world.root_node):
            self.get_coords()
            self.world.game.write('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                              'land height: {3}'.format(self.camX, self.camY, self.camZ,
                               self.land_z))

            print base.camera.getPos()

            for chunks_clt in self.chunks_clts.values():
                t = time.time()
                chunks_clt.generate()
                print 'Chunks generate: ', time.time() - t
                t = time.time()
                chunks_clt.show()
                print 'Chunks show: ', time.time() - t

    def create(self):
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = (x*self.max_len)+(self.max_len / 2), (y*self.max_len) + (self.max_len / 2), 0
                self.chunks_clts[name] = ChunksCollection(self, self.world, name, self.max_len)


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

