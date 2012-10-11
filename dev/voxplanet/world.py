#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import time

from panda3d.core import NodePath
from panda3d.core import TPLow
from panda3d.core import VBase3
from panda3d.core import Vec3
from pandac.PandaModules import Texture, TextureStage
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from voxplanet.landplane import LandNode, ChunkModel, TreeModel
from voxplanet.map2d import Map_generator_2D
from voxplanet.map3d import Map3d

#sys.setrecursionlimit(65535)

class Sky():
    def __init__(self):
        base.setBackgroundColor(0, 136, 255)

class WaterNode():
    """Water plane for nya

    """
    def __init__(self, config, water_z):
        self.config = config
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
        z = self.world.map3d[x, y]
        self.center = x, y, z
        self.hide()

    def repaint(self):
        if self.len_chunk > self.chunks_map.chunk_len:
            divide_dist = self.len_chunk
            #show_dist = self.chunks_map.far
            #print 'Center and char: ', self.center, self.chunks_map.charX, self.chunks_map.charY, self.chunks_map.camZ
            length_cam = VBase3.length(Vec3(self.center) - Vec3(self.chunks_map.charX,
                                                                self.chunks_map.charY,
                                                                self.chunks_map.camZ))
            if length_cam < divide_dist:
                self.divide()
            else:
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

    chunks = {}
    thread_done = True

    def __init__(self, chunks_map, world, center, size_world):

        self.center = center
        self.config = world.config

        self.size_world = size_world
        self.chunks_map = chunks_map

        self.world = world

        self.root = QuadroTreeNode(self, self.size_world, center = self.center)
        self.chunks_models = {}
        self.tree_models = {}

        self.generate()
        self.show()

    def generate(self):
        for chunk in self.chunks:
            self.chunks[chunk] = False
        #self.chunks = {}
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event

        for chunk in self.chunks:

            if self.chunks[chunk]:
                length_cam = VBase3.length(Vec3(chunk[0]) - Vec3(self.chunks_map.charX,
                                                                 self.chunks_map.charY,
                                                                 self.chunks_map.camZ))
                detach_dist = self.chunks_map.far
                if length_cam > detach_dist:
                    self.chunks[chunk] = False

            if self.chunks[chunk]:
                if not self.chunks_models.has_key(chunk):
                    self.chunks_models[chunk] = ChunkModel(self.config, self.world.map3d,
                                                           chunk[0][0], chunk[0][1], chunk[1],
                                                           self.chunks_map.chunk_len,
                                                           self.world.params.tex_uv_height,
                                                           self.world.params.chunks_tex
                                                           )

        for chunk_model in self.chunks_models:
            if self.chunks[chunk_model]:
                self.chunks_models[chunk_model].setX(self.chunks_map.DX)
                self.chunks_models[chunk_model].setY(self.chunks_map.DY)
                self.chunks_models[chunk_model].reparentTo(self.world.root_node)
            else:
                self.chunks_models[chunk_model].detachNode()


        #self.world.root_node.flattenLight()

class ChunksMap():
    def __init__(self, world, size, level):
        self.world = world
        self.config = world.config
        self.level = level
        self.size = size
        self.size_region = self.config.size_region
        self.size_world = self.config.size_world
        self.chunk_len = self.config.chunk_len
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
        d_charX = base.camera.getX(self.world.root_node) - self.camX
        d_charY = base.camera.getY(self.world.root_node) - self.camY
        self.camX, self.camY, self.camZ = base.camera.getPos(self.world.root_node)

        self.far = self.camZ*self.config.factor_far

        self.charX += d_charX
        self.charY += d_charY

        self.land_z = int(self.world.map3d[int(self.charX), int(self.charY)])

        if self.far < 1000:
            self.far = 1000
        base.camLens.setFar(self.far*2)

        self.test_coord()

    def test_coord(self):
        if self.charX < 0:
            self.charX = 0
        if self.charY < 0:
            self.charY = 0
        if self.charX >= self.size_world:
            self.charX = self.size_world - 1
        if self.charY >= self.size_world:
            self.charY = self.size_world - 1

        self.DX = (int(self.charX) / self.size_region) * self.size_region
        self.DY = (int(self.charY) / self.size_region) * self.size_region
        self.camX = self.charX - self.DX
        self.camY = self.charY - self.DY

        base.camera.setPos(self.world.root_node, (self.camX, self.camY, float(self.camZ)) )
        self.camPos = base.camera.getPos(self.world.root_node)

    def set_char_coord(self, coord):
        """Set char/cam coords

        coord - X, Y, Z
        """
        x, y, z = coord
        self.charX = x
        self.charY = y
        self.camZ = z

        self.test_coord()

        self.repaint()


    def repaint(self):
        self.get_coords()
        self.world.status('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                          'land height: {3} | Char: X: {4}, Y: {5}'.format(int(self.camX), int(self.camY), int(self.camZ),
                           self.land_z, int(self.charX), int(self.charY)))

        for chunks_clt in self.chunks_clts.values():
            chunks_clt.generate()
            chunks_clt.show()

    def show(self):
        if self.camPos != base.camera.getPos(self.world.root_node):
            self.repaint()

    def create(self):
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = (x*self.size_world)+(self.size_world / 2), (y*self.size_world) + (self.size_world / 2), 0
                self.chunks_clts[name] = ChunksCollection(self, self.world, name, self.size_world)


class World():
    def __init__(self, config, params):
        self.config = config
        self.params = params
        self.level = self.config.root_level
        self.seed = random.randint(0, sys.maxint)
        self.root_node = NodePath('Root_World')
        self.root_node.reparentTo(self.params.root_node)
        self.status = self.params.status

        #taskMgr.setupTaskChain('world_chain_create', numThreads = 1, tickClock = False,
                       #threadPriority = TPLow, frameBudget = 1)

        taskMgr.setupTaskChain('world_chain_show', numThreads = 1, tickClock = False,
                       threadPriority = TPLow, frameBudget = 1)

        self.trees = []

        #self.water = WaterNode(0.75)
        #self.water.show()

    def get_map3d_tex(self, size = 512, filename = None):
        return self.map3d.get_map_3d_tex(size, filename)

    def new(self):
        """New world
        """

        for tree in self.trees:
            tree.removeNode()
        self.trees = []
        for i in xrange(self.config.tree_models):
            self.trees.append(TreeModel(Vec3(4,4,7), self.params.tree_tex, self.params.leafModel))

        def create_world():
            global_map_gen = Map_generator_2D(self.config, self.seed)
            complete_i = 0
            st = 'Start generate of world'
            print st
            self.status(st)
            for e, (i, desc) in enumerate(global_map_gen.start()):
                st = '{0} * step: {1} / {2}'.format(e, i,desc)
                print st
                self.status(st)
                complete_i = i
            print global_map_gen.maps.get_ascii(3)
            st = 'Start convertation 2d -> 3d'
            print st
            self.status(st)
            self.map2d = global_map_gen.end_map
            # TODO: calculate real size of world
            self.map3d = Map3d(self.config, self.map2d, self.seed)
            endstr = 'Map generation process has been completed. Seed: {0}'.format(\
                                                self.seed)
            print endstr
            self.status(endstr)

        create_world()


        self.chunks_map = ChunksMap(self, 0, 1)
        self.chunks_map.set_char_coord((self.config.size_world/2, self.config.size_world/2, 10000))
        self.sky = Sky()
        taskMgr.add(self.show, 'WorldShow', taskChain = 'world_chain_show')

    def show(self, task):
        """Task for showing of world
        """
        self.chunks_map.show()
        time.sleep(0.2)
        return task.cont

# vi: ft=python:tw=0:ts=4

