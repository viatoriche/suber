#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import time
import threading

from panda3d.core import NodePath
from panda3d.core import TPLow, TPHigh
from panda3d.core import VBase3, VBase2
from panda3d.core import Vec3, Vec2
from panda3d.core import Mutex
from pandac.PandaModules import Texture, TextureStage
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from voxplanet.landplane import LandNode, ChunkModel, LowTreeModel, ForestNode
from voxplanet.map2d import Map_generator_2D
from voxplanet.map3d import Map3d
from voxplanet.support import profile_decorator
from voxplanet.treegen import TreeLand
from direct.stdpy import threading2 as panda_threading

#sys.setrecursionlimit(65535)

class Sky():
    def __init__(self):
        base.setBackgroundColor(0, 136, 255)

class WaterNode():
    """Water plane for nya

    config - voxplanet.config
    water_z - Z coord for water
    """
    def __init__(self, config, water_z):
        self.config = config
        self.water_z = water_z
        self.create(0, 0, (self.config.size_region/2, self.config.size_region/2))

    def create(self, x, y, scale):
        """create node

        x, y - start coords
        scale - size
        """
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
        """Show method
        """
        self.water.landNP.show()

    def hide(self):
        """Hide method
        """
        self.water.landNP.hide()

    def reset(self, x, y):
        """Show on new x, y coords
        """
        #self.Destroy()
        #self.create(x, y)
        self.water.landNP.show()
        try:
            self.water.landNP.setPos(x, y, self.water_z)
        except:
            pass

class QuadroTreeNode:
    """Node - one cube, which may divide on 4 chunks, when camera is near

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
            divide_dist = self.size * self.config.count_chunks
            length_cam = VBase3.length(Vec3(self.center) - Vec3(self.chunks_map.charX,
                                                                self.chunks_map.charY,
                                                                self.chunks_map.camZ))
            #length_cam = VBase2.length(Vec2(self.center[0], self.center[1]) - Vec2(self.chunks_map.charX,
                                                                #self.chunks_map.charY))

            if length_cam <= divide_dist:
                #print 'Divide: ', divide_dist, self.size, self.level, length_cam
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
    level_chunks = {}

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
        return

        self.mutex.acquire()
        t = time.time()
        try:
            sizes = []
            for chunk in self.chunks:
                if self.chunks[chunk]:
                    sizes.append(chunk[1])

            # calculate distance for remove chunks - LOD
            remove_far = min(sizes) * self.config.factor_remove_far

            to_remove = []
            for chunk in self.chunks:
                # if chunk was marked for show
                length_cam = VBase2.length(Vec2(chunk[0][0], chunk[0][1]) - Vec2(self.chunks_map.charX,
                                                                 self.chunks_map.charY
                                                                 ))
                # hide mark, if distance for chunk too long
                if length_cam >= remove_far:
                    to_remove.append(chunk)
                    if self.chunks_models.has_key(chunk):
                        self.chunks_models[chunk].removeNode()
                        del self.chunks_models[chunk]

            for chunk in to_remove:
                del self.chunks[chunk]

        except RuntimeError, e:
            print e

        print 'remove: ', time.time() - t
        self.mutex.release()

    #@profile_decorator
    def update(self, FarCreate = False):
        """Create and show chunk models
        """
        # TODO: add delete cube event

        # For get minimum size of visible chunks

        #if not Force:

            #if len(self.chunks_map.way) <= 1:
                #return False

            #start = self.chunks_map.way[0]
            #end = self.chunks_map.way[-1:][0]

            #dist = VBase3.length(start - end)

            #print dist, (self.far / self.config.factor_far) * (self.config.count_chunks / 2)

            #if dist < (self.far / self.config.factor_far) * (self.config.count_chunks / 2):
                #return False

        self.mutex.acquire()

        t = time.time()

        our_height = abs(self.chunks_map.camZ - self.chunks_map.land_z)
        for i in xrange(self.config.min_level, self.config.size_mod):
            if our_height <= 2 ** i:
                our_level = i
                break


        def create_chunk(far):

            for our_level in our_levels:

                for chunk in self.chunks[our_level]:
                    if self.status_chunks[chunk]:
                        center, size, level = chunk
                        length_cam = VBase2.length(Vec2(center[0], center[1]) - Vec2(self.chunks_map.charX,
                                                                         self.chunks_map.charY
                                                                         ))
                        # hide mark, if distance for chunk too long
                        if length_cam > far:
                            self.status_chunks[chunk] = False
                        if length_cam <= far:
                            if not self.chunks_models.has_key(chunk):
                                self.chunks_models[chunk] = ChunkModel(self.config, self.world.map3d,
                                                               center[0], center[1], size,
                                                               self.chunks_map.chunk_len,
                                                               self.world.params.tex_uv_height,
                                                               self.world.params.chunks_tex
                                                               )
                                #return True
            return False


        if not FarCreate:

            for chunk in self.status_chunks:
                self.status_chunks[chunk] = False

            self.generate(our_level)
            self.our_chunks = []

            lim_level = our_level + self.config.count_levels

            if lim_level > self.config.size_mod:
                lim_level = self.config.size_mod

            our_levels = range(our_level, lim_level)


            # calculate distance for show or hide chunks - LOD
            self.far = (2 ** max(our_levels)) * self.config.count_chunks
            self.world.params.fog.setLinearRange(0, self.far)
            base.camLens.setFar(self.far)

            try:
                tree_chunks = self.chunks[self.config.tree_level]
                for chunk in tree_chunks:
                    center, size, level = chunk
                    length_cam = VBase2.length(Vec2(center[0], center[1]) - Vec2(self.chunks_map.charX,
                                                                     self.chunks_map.charY
                                                                     ))
                    # hide mark, if distance for chunk too long
                    if length_cam <= size:
                        self.world.forest.add_trees(chunk)
            except KeyError, e:
                pass


            add_new = create_chunk(self.far)

            if add_new == False:
                self.chunks_map.add_done = True

            print 'update: ', time.time() - t
        else:
            self.chunks_map.add_far_done = True

        self.mutex.release()
        return True

    #@profile_decorator
    def repaint(self):
        """attach/detach -> hide/show models
        """
        self.mutex.acquire()
        t = time.time()

        for chunk in self.chunks_models:
            if self.status_chunks[chunk]:
                self.chunks_models[chunk].setX(self.chunks_map.DX)
                self.chunks_models[chunk].setY(self.chunks_map.DY)
                if self.chunks_models[chunk].getParent() != self.world.root_node:
                    self.chunks_models[chunk].reparentTo(self.world.root_node)

        for chunk in self.chunks_models:
            if not self.status_chunks[chunk]:
                if self.chunks_models[chunk].getParent() == self.world.root_node:
                    self.chunks_models[chunk].detachNode()

        print 'repaint: ', time.time() - t

        self.mutex.release()

    #@profile_decorator
    def repaint_forest(self):
        t = time.time()
        self.forest.show_forest(self.chunks_map.DX, self.chunks_map.DY, self.far/2, self.config.tree_far,
                                                                (
                                                                 self.chunks_map.charX,
                                                                 self.chunks_map.charY,
                                                                 self.chunks_map.camZ
                                                                ),
                                                                self.config.tree_far * self.config.tree_billboard)
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
        base.camera.setPos(0, 0, 10000)
        self.camPos = base.camera.getPos(self.world.root_node)
        self.charX = 0
        self.charY = 0
        self.camX = 0
        self.camY = 0
        self.DX = 0
        self.DY = 0
        self.way = []
        taskMgr.setupTaskChain('world_chain_generate', numThreads = 1,
                       frameSync = False, threadPriority = TPHigh, timeslicePriority = False)
        #taskMgr.setupTaskChain('world_chain_repaint', numThreads = 1,
                       #frameSync = True, timeslicePriority = True)
        taskMgr.setupTaskChain('world_forest_repaint', numThreads = 1,
                       frameSync = True, threadPriority = TPLow, timeslicePriority = True)
        taskMgr.setupTaskChain('cam_check_chain', numThreads = 1,
                       frameSync = True, timeslicePriority = True)
        self.removed = False
        self.add_done = False
        self.add_far_done = False
        self.need_repaint = False
        self.need_forest = False
        self.need_update = False
        self.get_coords()
        self.create()

    def get_coords(self):
        """Get charX, charY coords from camera
        """
        d_charX = base.camera.getX(self.world.root_node) - self.camX
        d_charY = base.camera.getY(self.world.root_node) - self.camY
        coord = base.camera.getPos(self.world.root_node)
        self.camX, self.camY, self.camZ = coord
        self.way.append(coord)

        #self.far = self.camZ*self.config.factor_far

        self.charX += d_charX
        self.charY += d_charY

        self.land_z = int(self.world.map3d[int(self.charX), int(self.charY)])

        #if self.far < 1000:
            #self.far = 1000
        #base.camLens.setFar(self.far*2)

        self.test_coord()

    def test_coord(self):
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

        self.DX = (int(self.charX) / self.size_region) * self.size_region
        self.DY = (int(self.charY) / self.size_region) * self.size_region
        self.camX = self.charX - self.DX
        self.camY = self.charY - self.DY

        base.camera.setPos(self.world.root_node, (self.camX,
                                     self.camY,
                                     float(self.camZ)) )
        self.camPos = base.camera.getPos(self.world.root_node)

    def set_char_coord(self, coord):
        """Set char/cam coords -> teleportation

        coord - X, Y, Z
        """
        x, y, z = coord
        self.charX = x
        self.charY = y
        self.camZ = z

        self.test_coord()

        self.regen(FarCreate = False)
        self.repaint()
        self.repaint_forest()

    #@profile_decorator
    def repaint(self):
        """repaint all chunks
        """
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.repaint()

    def repaint_forest(self):
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.repaint_forest()

    def repaint_forest_task(self, task):
        if self.need_forest:
            self.repaint_forest()
            self.need_forest = False
        return task.again

    def remove_far(self):
        """repaint all chunks
        """
        for chunks_clt in self.chunks_clts.values():
            chunks_clt.remove_far()

    def regen(self, FarCreate = False):
        res = False
        for chunks_clt in self.chunks_clts.values():
            if chunks_clt.update(FarCreate):
                res = True
        return res


    def regen_task(self, task):
        if not self.add_done:
            self.regen(FarCreate = False)
            self.repaint()
            return task.cont
            #self.regen(FarCreate = True)
        return task.again

    def cam_check(self, task):
        """check cam for update

        """
        if self.camPos != base.camera.getPos(self.world.root_node):
            self.get_coords()
            self.world.status('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                      'land height: {3} | Char: X: {4}, Y: {5}'.format(
                       int(self.camX), int(self.camY), int(self.camZ),
                       self.land_z, int(self.charX), int(self.charY)))
            self.add_done = False
            self.add_far_done = False
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

        taskMgr.doMethodLater(self.config.chunk_delay, self.regen_task, 'WorldRegen', taskChain = 'world_chain_generate')
        taskMgr.doMethodLater(5, self.repaint_forest_task, 'WorldRepaintForest', taskChain = 'world_forest_repaint')
        taskMgr.doMethodLater(0.1, self.cam_check, 'cam_check', taskChain = 'cam_check_chain')


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
        self.root_node.reparentTo(self.params.root_node)
        self.gui = self.params.gui
        self.status = self.params.status

        self.mutex_repaint = Mutex('repaint')
        self.trees = []
        self.treeland = TreeLand(self.config, self)
        self.forest = None

    def get_map3d_tex(self, size = 512, filename = None):
        """Generate texture of map world
        """
        return self.map3d.get_map_3d_tex(size, filename)

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


        self.chunks_map = ChunksMap(self, 0, 1)
        #self.chunks_map.set_char_coord((self.config.size_world/2, self.config.size_world/2, 10000))
        self.chunks_map.set_char_coord((30000, 30000, 300))
        self.sky = Sky()

# vi: ft=python:tw=0:ts=4

