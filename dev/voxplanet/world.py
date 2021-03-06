#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import math
import random
import sys
import time

from panda3d.core import Mutex
from panda3d.core import NodePath
from panda3d.core import TPLow, TPHigh
from panda3d.core import VBase3, VBase2
from panda3d.core import Vec3, Vec2
from pandac.PandaModules import Texture, TextureStage
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from voxplanet.landplane import LandNode, ChunkModel, LowTreeModel, ForestNode, TreeModel, Voxels
from voxplanet.map2d import Map_generator_2D
from voxplanet.map3d import Map3d
from voxplanet.support import profile_decorator
from voxplanet.treegen import TreeLand

#sys.setrecursionlimit(65535)


class QuadroTreeNode:
    """Node - one cube, which may divide on 4 chunks, when char is near

    chunks_clt - ChunksCollection()
    size - size of chunk
    parent - parent QuadroNode
    level - deep level to world
    center - coordinates of center chunk
    """
    # exist = True #make voxel deletable by player
    def __init__(self, chunks_clt, size, parent=None,\
                       level = None, center = (0,0,0)):

        self.parent = parent
        self.chunks_clt = chunks_clt
        self.world = chunks_clt.world
        self.config = chunks_clt.config
        if level == None:
            level = self.config.size_mod
        self.level = level
        self.chunks_map = chunks_clt.chunks_map
        self.size = size
        self.childs = {}
        x = center[0]
        y = center[1]
        z = self.world.map3d[x, y]
        self.center = x, y, z
        self.add()
        self.mark_hide()

    def repaint(self, level):
        """divide or mark to show this chunk node, depend - distance to char coords
        """
        if self.level > level:
            #divide_dist = self.config.chunk_len * (3 ** (25 - self.level))
            #show_dist = self.chunks_map.far
            s2 = self.size * self.size
            s2 += s2
            divide_dist = math.sqrt(s2)
            length = VBase3.length(Vec3(self.center) - Vec3(self.chunks_map.charX,
                                                                self.chunks_map.charY,
                                                                self.chunks_map.charZ))
            #length = VBase2.length(Vec2(self.center[0], self.center[1]) - Vec2(self.chunks_map.charX,
                                                                #self.chunks_map.charY))

            if length <= divide_dist:
                #print 'Divide: ', divide_dist, self.size, self.level, length
                self.divide(level)
            else:
                self.mark_show()
        else:
            self.mark_show()

    def divide(self, level):
        """divide this chunk on 4 chunks
        """
        if self.childs == {}:
            new_size = self.size/2
            new_center = self.size/4
            new_level = self.level - 1
            # <- up
            name = self.center[0] - new_center, self.center[1] - new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_size, self, \
                    new_level, name)
            self.childs[name].repaint(level)
            # -> up
            name = self.center[0] + new_center, self.center[1] - new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_size, self, \
                    new_level, name)
            self.childs[name].repaint(level)
            # <- down
            name = self.center[0] - new_center, self.center[1] + new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_size, self, \
                    new_level, name)
            self.childs[name].repaint(level)
            # -> down
            name = self.center[0] + new_center, self.center[1] + new_center, 0
            self.childs[name] = QuadroTreeNode(self.chunks_clt, new_size, self, \
                    new_level, name)
            self.childs[name].repaint(level)
        else:
            for child in self.childs:
                self.childs[child].repaint(level)

    def add(self):
        if not self.chunks_clt.chunks.has_key(self.level):
            self.chunks_clt.chunks[self.level] = []

        self.chunks_clt.chunks[self.level].append( (self.center, self.size, self.level) )

    def mark_show(self):
        self.chunks_clt.status_chunks[self.center, self.size, self.level] = True

    def mark_hide(self):
        self.chunks_clt.status_chunks[self.center, self.size, self.level] = False

class ChunksCollection():
    """Collection of chunks quadro tree nodes

    chunks_map - ChunksMap()
    world - World()
    center - center for start QuadroTree node
    size_world - size of world - first size of chunk
    """
    # chunks[level] = center, size
    chunks = {}
    status_chunks = {}

    def __init__(self, chunks_map, world, center, size_world):

        self.center = center
        self.config = world.config

        self.size_world = size_world
        self.chunks_map = chunks_map

        self.world = world
        self.our_chunks = []

        self.root = QuadroTreeNode(self, self.size_world, center = self.center)
        self.chunks_models = {}
        self.forest = self.world.forest
        self.mutex = self.world.mutex_repaint

    #@profile_decorator
    def generate(self, level):
        """generate of all childs
        """
        t = time.time()
        self.root.repaint(level)
        print 'generate: ', time.time() - t

    #@profile_decorator
    def remove_far(self):
        """Remove far chunk models
        """
        # TODO: add delete cube event

        # For get minimum size of visible chunks

        t = time.time()
        chunks = self.chunks_models.keys()

        # calculate distance for remove chunks - LOD
        remove_far = self.far * 3

        for chunk in chunks:
            # if chunk was marked for show
            length = VBase2.length(Vec2(chunk[0][0], chunk[0][1]) - Vec2(self.chunks_map.charX,
                                                             self.chunks_map.charY
                                                             ))
            # hide mark, if distance for chunk too long
            if length >= remove_far:
                if self.chunks_models.has_key(chunk):
                    self.mutex.acquire()
                    self.chunks_models[chunk].removeNode()
                    del self.chunks_models[chunk]
                    del self.status_chunks[chunk]
                    self.mutex.release()

        print 'remove: ', time.time() - t

    @profile_decorator
    def update(self, Force = False):
        """Create and show chunk models
        """
        # TODO: add delete cube event

        # For get minimum size of visible chunks

        t = time.time()

        our_height = abs(self.chunks_map.charZ - self.chunks_map.land_z)
        for i in xrange(self.config.min_level, self.config.size_mod):
            if our_height <= 2 ** i:
                our_level = i
                break


        def create_chunk(far):

            for our_level in our_levels:
                for chunk in self.chunks[our_level]:
                    if self.status_chunks.has_key(chunk):
                        if self.status_chunks[chunk]:
                            center, size, level = chunk
                            length = VBase2.length(Vec2(center[0], center[1]) - Vec2(self.chunks_map.charX,
                                                                             self.chunks_map.charY
                                                                             ))
                            # hide mark, if distance for chunk too long
                            if length > far:
                                self.status_chunks[chunk] = False
                            if length <= far:
                                if not self.chunks_models.has_key(chunk):
                                    self.mutex.acquire()
                                    self.chunks_models[chunk] = ChunkModel(self.config, self.world.map3d,
                                                                   self.world.voxels,
                                                                   center[0], center[1], size,
                                                                   self.chunks_map.chunk_len,
                                                                   self.world.params.chunks_tex,
                                                                   self.world.params.water_tex
                                                                   )
                                    self.mutex.release()
                                    if not Force:
                                        time.sleep(self.config.chunk_sleep)

        for chunk in self.status_chunks:
            self.status_chunks[chunk] = False

        self.generate(our_level)
        land_level = 0

        if self.config.low_mount_level[1] >= self.chunks_map.land_z >= self.config.low_mount_level[0]:
            land_level = 1

        if self.config.mid_mount_level[1] >= self.chunks_map.land_z >= self.config.mid_mount_level[0]:
            land_level = 2

        if self.config.high_mount_level[1] >= self.chunks_map.land_z >= self.config.high_mount_level[0]:
            land_level = 3

        lim_level = our_level + self.config.count_levels[land_level]

        if lim_level > self.config.size_mod:
            lim_level = self.config.size_mod

        our_levels = range(our_level, lim_level)

        # calculate distance for show or hide chunks - LOD
        self.far = (2 ** max(our_levels)) * 2
        self.world.params.fog.setLinearRange(0, self.far)
        self.world.gui.camLens.setFar(self.far * 2)

        t = time.time()
        try:
            tree_chunks = self.chunks[self.config.tree_level]
            for chunk in tree_chunks:
                center, size, level = chunk
                length = VBase2.length(Vec2(center[0], center[1]) - Vec2(self.chunks_map.charX,
                                                                 self.chunks_map.charY
                                                                 ))
                # hide mark, if distance for chunk too long
                if length <= size:
                    self.world.forest.add_trees(chunk)
        except KeyError, e:
            pass

        print 'add new trees: ', time.time() - t

        t = time.time()
        create_chunk(self.far)
        print 'create chunks: ', time.time() - t

    #@profile_decorator
    def repaint(self):
        """attach/detach -> hide/show models
        """
        t = time.time()

        for chunk in self.chunks_models:
            if self.status_chunks[chunk]:
                self.chunks_models[chunk].setX(self.chunks_map.DX)
                self.chunks_models[chunk].setY(self.chunks_map.DY)
                if self.chunks_models[chunk].getParent() != self.world.root_node:
                    self.mutex.acquire()
                    self.chunks_models[chunk].reparentTo(self.world.root_node)
                    self.mutex.release()

        for chunk in self.chunks_models:
            if not self.status_chunks[chunk]:
                if self.chunks_models[chunk].getParent() == self.world.root_node:
                    self.mutex.acquire()
                    self.chunks_models[chunk].detachNode()
                    self.mutex.release()

        print 'repaint: ', time.time() - t


    #@profile_decorator
    def repaint_forest(self, Force = False):
        t = time.time()
        self.forest.show_forest(self.chunks_map.DX, self.chunks_map.DY, self.far, self.config.tree_far,
                                                                (
                                                                 self.chunks_map.charX,
                                                                 self.chunks_map.charY,
                                                                 self.chunks_map.charZ
                                                                ),
                                                                Force = Force
                                                                )
        print 'forest: ', time.time() - t



class ChunksMap():
    """All chunks collections here

    world - World()
    size - count of chunks_collection
    level - start level // deprecated
    """
    def __init__(self, world, size, level):
        self.world = world
        self.config = world.config
        self.level = level
        self.size = size
        self.size_region = self.config.size_region
        self.size_world = self.config.size_world
        self.chunk_len = self.config.chunk_len
        self.chunks_clts = {}
        self.charPos = self.world.avatar.getPos(self.world.root_node)
        self.charX = 0
        self.charY = 0
        self.charRX = 0
        self.charRY = 0
        self.DX = 0
        self.DY = 0
        taskMgr.setupTaskChain('world_chain_generate', numThreads = 1,
                       frameSync = False, threadPriority = TPLow, timeslicePriority = False)
        taskMgr.setupTaskChain('world_forest_repaint', numThreads = 1,
                       frameSync = False, threadPriority = TPLow, timeslicePriority = False)
        taskMgr.setupTaskChain('char_check_chain', numThreads = 1,
                       frameSync = False, timeslicePriority = False)
        self.add_done = False
        self.need_forest = False
        self.need_remove = False
        self.create()

    def get_coords(self):
        """Get charX, charY coords from camera
        """
        d_charX = self.world.avatar.getX(self.world.root_node) - self.charRX
        d_charY = self.world.avatar.getY(self.world.root_node) - self.charRY
        coord = self.world.avatar.getPos(self.world.root_node)
        self.charRX, self.charRY, self.charZ = coord

        self.charX += d_charX
        self.charY += d_charY

        self.test_coord()

    def charSetPos(self, Force):
        self.regen(Force = True)
        self.repaint()
        self.world.forest.clear()
        if not Force:
            self.need_forest = True
        else:
            self.repaint_forest(True)

        self.world.avatar.setPos(self.world.root_node, (self.charRX,
                                     self.charRY,
                                     float(self.charZ)) )

    def test_coord(self, Force = False):
        """Test and fix char coords, DX, DY, change new cam coords, if need
        """
        if self.charX < 0:
            self.charX = 0
        if self.charY < 0:
            self.charY = 0
        if self.charX >= self.size_world:
            self.charX = self.size_world - 1
        if self.charY >= self.size_world:
            self.charY = self.size_world - 1

        newDX = (int(self.charX) / self.size_region) * self.size_region
        newDY = (int(self.charY) / self.size_region) * self.size_region

        self.charRX = self.charX - newDX
        self.charRY = self.charY - newDY

        self.land_z = int(self.world.map3d[int(self.charX), int(self.charY)])
        self.charPos = self.world.avatar.getPos(self.world.root_node)

        if newDX != self.DX or newDY != self.DY or Force:
            self.DX = newDX
            self.DY = newDY
            self.charSetPos(Force)


    def set_char_coord(self, coord):
        """Set char/cam coords -> teleportation

        coord - X, Y, Z
        """
        self.charX, self.charY, self.charZ = coord
        self.test_coord(Force = True)

    #@profile_decorator
    def repaint(self):
        """repaint all chunks
        """
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.repaint()

    def repaint_forest(self, Force):
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.repaint_forest(Force)

    def repaint_forest_task(self, task):
        if self.need_forest:
            self.repaint_forest(False)
            self.need_forest = False
        return task.again

    def remove_far(self):
        """repaint all chunks
        """
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.remove_far()

    def regen(self, Force = False):
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.update(Force)


    def regen_task(self, task):
        if not self.add_done:
            self.regen()
            self.repaint()
            self.add_done = True
            self.need_remove = True
            return task.cont
        elif self.need_remove:
            self.remove_far()
            self.need_remove = False
        return task.again

    def char_check(self, task):
        """check cam for update

        """
        if self.charPos != self.world.avatar.getPos(self.world.root_node):
            self.get_coords()
            self.world.status('rX: {0}, rY: {1}, Z: {2}, '\
                      'land z: {3} | wX: {4}, wY: {5}'.format(
                       int(self.charRX), int(self.charRY), int(self.charZ),
                       self.land_z, int(self.charX), int(self.charY)))
            self.add_done = False
            self.need_forest = True
        return task.again

    def create(self):
        """Create of all chunks collections
        """
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = (x*self.size_world)+(self.size_world / 2),\
                       (y*self.size_world) + (self.size_world / 2), 0
                self.chunks_clts[name] = ChunksCollection(self,
                                          self.world, name, self.size_world)

        coord = self.config.size_world/2, self.config.size_world/2, 10000
        self.set_char_coord(coord)

        taskMgr.doMethodLater(self.config.chunk_delay, self.regen_task, 'WorldRegen', taskChain = 'world_chain_generate')
        taskMgr.doMethodLater(self.config.tree_delay, self.repaint_forest_task, 'WorldRepaintForest', taskChain = 'world_forest_repaint')
        taskMgr.doMethodLater(0.01, self.char_check, 'char_check', taskChain = 'char_check_chain')


class World():
    """World

    config - voxplanet.config.Config()
    params - voxplanet.params.Params()
    """
    def __init__(self, config, params):
        self.config = config
        self.params = params
        self.seed = random.randint(0, sys.maxint)
        self.root_node = NodePath('Root_World')
        self.change_params(params)

        self.mutex_repaint = Mutex('repaint')
        self.trees = []
        self.treeland = TreeLand(self.config, self)
        self.forest = None

    def change_params(self, params):
        self.params = params
        self.root_node.reparentTo(self.params.root_node)
        self.gui = self.params.gui
        self.avatar = self.params.avatar
        self.status = self.params.status

    def get_map3d_tex(self, size = 512, filename = None):
        """Generate texture of map world
        """
        return self.map3d.get_map_3d_tex(size, filename, (self.chunks_map.charX,
                                                          self.chunks_map.charY))

    def create_trees(self):
        for tree in self.trees:
            tree.removeNode()
        self.trees = []
        for i in xrange(self.config.tree_models):
            l = 1
            self.trees.append(LowTreeModel('tree_{0}'.format(i),
                                 (l, l, random.randint(8, 32)),
                                 self.params.tree_tex,
                                 self.params.leafTex
                                 ))
            #self.trees.append(TreeModel(self, 'tree_{0}'.format(i),
                                        #Vec3(l,
                                             #l,
                                             #random.randint(2,4)),
                                        #self.params.tree_tex,
                                        #self.params.leafModel,
                                        #self.params.leafTex,
                                        #numIterations = 0,
                                        #numCopies = 0))

        #for i in xrange(self.config.tree_models):
            #self.trees.append(CubeModel(1, 1, random.randint(6,18)))
            #self.trees[i].setTexture(self.params.tree_tex)
            #self.trees[i].flattenStrong()
        self.forest = ForestNode(self.config, self)
        self.forest.reparentTo(self.root_node)

    def new(self):
        """New world
        """

        self.create_trees()

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

        self.voxels = Voxels(self.map3d, self.params.get_coord_block)

        self.chunks_map = ChunksMap(self, 0, 1)

# vi: ft=python:tw=0:ts=4

