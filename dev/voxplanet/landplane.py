#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Land classes - chunks, LandPlane, trees
"""

import random, time

from panda3d.core import Geom, GeomNode
from panda3d.core import GeomVertexData
from panda3d.core import GeomTriangles, GeomVertexWriter
from panda3d.core import GeomVertexFormat
from panda3d.core import Vec3, Vec2
from panda3d.core import VBase3, VBase2, BitMask32
from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import TextureStage
from pandac.PandaModules import TransparencyAttrib
from voxplanet.support import make_square4v
from voxplanet.treegen import make_fractal_tree, treeform
from pandac.PandaModules import UnalignedLVecBase4f as UVec4
from pandac.PandaModules import PTA_LVecBase4f as PTAVecBase4
from pandac.PandaModules import Shader
from panda3d.core import RigidBodyCombiner as RBC
from voxplanet.shapeGenerator import Cube as CubeModel
from voxplanet.support import profile_decorator
from pandac.PandaModules import CollisionNode, CollisionPolygon

class LandNode(NodePath):
    """Water / Land

    just square
    """
    def __init__(self, sx, sy, z, length):
        maker = CardMaker( 'land' )
        NodePath.__init__(self, maker.generate())
        #self.landNP = render.attachNewNode(maker.generate())
        self.setHpr(0,-90,0)
        self.setPos(sx, sy, z)
        self.setScale(length, 0, length)

class WaterNode(LandNode):
    """Water plane for nya

    config - voxplanet.config
    water_z - Z coord for water
    """
    def __init__(self, sx, sy, length, tex):
        LandNode.__init__(self, sx, sy, 0.5, length)
        ts = TextureStage('ts')
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setTexture(ts, tex)
        self.setTexScale(ts, 10000, 10000)


class LowTreeModel(NodePath):
    """Cube-like tree
    """
    def __init__(self, name, size, body_tex = None, leaf_tex = None):
        NodePath.__init__(self, name)
        self.name = name
        self.size = size
        self.body_tex = body_tex
        self.leaf_tex = leaf_tex
        self.make()
        self.flattenStrong()

    def make(self):
        self.body = CubeModel(*self.size)
        self.body.geom_node.setIntoCollideMask(BitMask32.bit(2))
        self.body.reparentTo(self)
        self.body.setTag('Tree', '{0}'.format(self.name))
        self.set_body_tex(self.body_tex)
        start_leaf = random.randint(2, 4)
        if start_leaf > self.size[2]-1:
            start_leaf = self.size[2]-1

        self.leafs = []
        i = 0
        for z in xrange(start_leaf, self.size[2]-1):
            for ix in xrange(-1, 1):
                for iy in xrange(-1, 1):

                    size_x = random.randint(int((self.size[2] - z + 4)*0.2),int((self.size[2] - z + 4)*0.4))
                    size_y = random.randint(int((self.size[2] - z + 4)*0.2),int((self.size[2] - z + 4)*0.4))
                    if size_x == 0 or size_y == 0:
                        continue
                    self.leafs.append(CubeModel(size_x, size_y, 1))
                    x = size_x * ix
                    y = size_y * iy

                    self.leafs[i].setPos(x, y, z)
                    self.leafs[i].reparentTo(self)
                    i += 1

        self.set_leaf_tex(self.leaf_tex)

    def set_body_tex(self, body_tex):
        if body_tex != None:
            self.body.setTexture(body_tex)

    def set_leaf_tex(self, leaf_tex):
        if leaf_tex != None:
            ts = TextureStage('ts')
            for leaf in self.leafs:
                leaf.setTexture(ts, leaf_tex)
                leaf.setTexScale(ts, 10, 10)
                leaf.setTransparency(TransparencyAttrib.MAlpha)


class TreeModel(NodePath):

    def __init__(self, world, name, length, tex, leafModel, leafTex,
                 pos=Vec3(0, 0, 0), numIterations = 11,
                 numCopies = 6, vecList=[Vec3(0,0,1),
                 Vec3(1,0,0), Vec3(0,-1,0)]):

        NodePath.__init__(self, name)

        self.world = world
        self.gui = self.world.gui
        self.bodydata=GeomVertexData("body vertices", treeform, Geom.UHStatic)
        self.length = length
        self.pos = pos
        self.numIterations = numIterations
        self.numCopies = numCopies
        self.vecList = vecList
        self.tex = tex
        self.leafModel = leafModel
        self.leafTex = leafTex
        make_fractal_tree(self.bodydata, self, self.length)
        self.setTexture(self.tex, 1)
        self.flattenStrong()
        #self.buff = self.gui.win.makeCubeMap(name, 64, self)

class ForestNode(NodePath):

    def __init__(self, config, world):
        NodePath.__init__(self, 'ForestNode')
        self.config = config
        self.world = world
        self.added = []
        self.trees = {}
        self.trees_in_node = 10
        self.mutex = self.world.mutex_repaint
        self.flatten_node = NodePath('flatten_nodes')

    def add_trees(self, chunk):
        # level
        if chunk not in self.added:
            self.added.append(chunk)
        else:
            return

        size2 = chunk[1] / 2
        x = chunk[0][0]
        y = chunk[0][1]
        sx = x - size2
        sy = y - size2
        ex = x + size2
        ey = y + size2

        t = time.time()
        trees = self.world.treeland[sx, sy, ex, ey]
        for tree in trees:
            if not self.trees.has_key(tree):
                self.trees[tree] = []
            self.trees[tree] = self.trees[tree] + trees[tree]

    def clear(self):
        self.flatten_node.detachNode()
        self.flatten_node.removeNode()
        self.flatten_node = NodePath('flatten_nodes')

    def show_forest(self, DX, DY, char_far, far, charpos, Force = False):
        """Set to new X

        center X - self.size/2 - DX
        """

        tmp_node = NodePath('tmp')
        self.flatten_node.copyTo(tmp_node)
        self.mutex.acquire()
        tmp_node.reparentTo(self)
        self.flatten_node.removeNode()
        self.mutex.release()
        self.tree_nodes = []
        self.flatten_node = NodePath('flatten_nodes')

        t = time.time()
        count_trees = 0
        for tree_n in self.trees:
            # create or attach
            for coord in self.trees[tree_n]:
                #length_cam_2d = VBase2.length(Vec2(coord[0], coord[1]) - Vec2(charpos[0], charpos[1]))
                length_cam_3d = VBase3.length(Vec3(coord) - Vec3(charpos))
                if char_far >= length_cam_3d <= far:
                    tree = self.world.trees[tree_n]
                    self.tree_nodes.append(NodePath('TreeNode'))
                    tree.copyTo(self.tree_nodes[count_trees])
                    x, y, z = coord
                    self.tree_nodes[count_trees].setPos(x - DX, y - DY, z-1)
                    count_trees += 1

        print 'Attach detach loop: ', time.time() - t

        if count_trees == 0:
            self.mutex.acquire()
            tmp_node.removeNode()
            self.mutex.release()
            return

        t = time.time()

        self.count_f_nodes = (count_trees / self.trees_in_node)+1
        self.flatten_nodes = [NodePath('flatten_node') for i in xrange(self.count_f_nodes)]
        s = 0
        e = self.trees_in_node
        added = 0
        for node in self.flatten_nodes:
            t_nodes = self.tree_nodes[s : e]
            s += self.trees_in_node
            e += self.trees_in_node
            for t_node in t_nodes:
                t_node.reparentTo(node)
                added += 1
            node.flattenStrong()
            if not Force:
                time.sleep(self.config.tree_sleep)
            node.reparentTo(self.flatten_node)
            if added == count_trees:
                break

        print 'Added: ', added, time.time() - t

        t = time.time()
        self.flatten_node.flattenStrong()
        self.mutex.acquire()
        self.flatten_node.reparentTo(self)
        tmp_node.removeNode()
        self.mutex.release()
        print 'flatten all trees: ', time.time() - t


class Voxel():
    def __init__(self, empty, block):
        self.empty = empty
        self.block = block
        self.get_top_uv = self.block.get_top_uv
        self.get_left_uv = self.block.get_left_uv
        self.get_right_uv = self.block.get_right_uv
        self.get_front_uv = self.block.get_front_uv
        self.get_back_uv = self.block.get_back_uv
        self.get_bottom_uv = self.block.get_bottom_uv

    def __call__(self):
        return self.empty

class VoxelsCleaner():
    def __init__(self, voxels):
        self.voxels = voxels

    def clean(self, time_clean = 5):
        curtime = time.time()
        try:
            keys = [key for key in self.voxels.cache if curtime - self.voxels.cache[key][1] > time_clean \
                                                 and not self.voxels.cache[key][2]]
        except RuntimeError:
            return
        for key in keys:
            del self.voxels.cache[key]

class Voxels(dict):
    cache = {}
    count_requests = 0
    time_clean = 2
    clean_count = 2 ** 18
    def __init__(self, heights, get_coord_block):
        self.heights = heights
        self.get_coord_block = get_coord_block
        self.repaint = []
        self.cleaner = VoxelsCleaner(self)

    def __setitem__(self, key, voxel):
        if key in self.cache:
            self.repaint.append(key)
        self.cache[key] = [voxel, time.time(), True]
        self.count_requests += 1
        if self.count_requests == self.clean_count:
            self.count_requests = 0
            self.cleaner.clean(self.time_clean)

    def check_repaint(self, chunk):
        center, size, level = chunk
        # TODO: check chunk for repaint
        return False

    def __getitem__(self, key):
        if key in self.cache:
            self.cache[key][1] = time.time()
            if self.count_requests == self.clean_count:
                self.count_requests = 0
                self.cleaner.clean(self.time_clean)
            return self.cache[key][0]
        else:
            empty = self.heights.check_empty(key)
            block = self.get_coord_block(key)
            vox = Voxel(empty, block)
            self.cache[key] = [vox, time.time(), False]
            self.count_requests += 1
            if self.count_requests == self.clean_count:
                self.count_requests = 0
                self.cleaner.clean(self.time_clean)
            return vox

class ChunkModel(NodePath):
    """Chunk for quick render and create voxel-objects

    config - config of voxplanet
    heights - {(centerX, centerY): height, (X2, Y2: height, ... (XN, YN): height}
    centerX, centerY - center coordinates
    size - size of chunk (in scene coords)
    chunk_len - count of voxels
    tex_uv_height - function return of uv coordinates for height voxel
    tex - texture map
    """

    v_format = GeomVertexFormat.getV3n3t2()

    # quads orientations
    QTOP = 0
    QLEFT = 1
    QRIGHT = 2
    QFRONT = 3
    QBACK = 4
    QBOTTOM = 5
    QSELF = 6

    def __init__(self, config, status_chunks, heights, voxels, chunk, tex, water_tex, dirt = False):
        NodePath.__init__(self, 'ChunkModel')
        self.dirt = dirt
        self.config = config
        self.heights = heights
        self.voxels = voxels
        self.status_chunks = status_chunks
        self.chunk = chunk
        self.center, self.size, self.level = chunk
        self.centerX, self.centerY, self.centerZ = map(lambda x: int(x), self.center)
        self.tex = tex
        self.water_tex = water_tex
        self.chunk_len = self.config.chunk_len
        self.size_voxel = self.size / self.chunk_len
        if self.size_voxel <1:
            self.size_voxel = 1
        self.size2 = self.size / 2
        self.start_x = self.centerX - self.size2
        self.start_y = self.centerY - self.size2
        self.start_z = self.centerZ - self.size2
        self.round_chunks = {}

        self.level_3d = self.config.level_3d

        self.v_data = GeomVertexData('chunk', self.v_format, Geom.UHStatic)

        #if self.start_z <= 0:
            #self.water = WaterNode(0, 0, self.size, self.water_tex)
            #self.water.setTwoSided(True)
            #self.water.reparentTo(self)

        self.end_z = self.start_z + self.size
        self.created = False
        if not self.dirt:
            land_in_chunk = False
            for x in xrange(self.start_x, self.start_x + self.size, self.size_voxel):
                for y in xrange(self.start_y, self.start_y + self.size, self.size_voxel):
                    if self.end_z >= self.heights[x, y] >= self.start_z:
                        self.created = self.create()
                        land_in_chunk = True
                        break
                if land_in_chunk:
                    break
        else:
            self.created = self.create()

    def round_chunk_level(self, orientation):
        if orientation in self.round_chunks:
            return self.round_chunks[orientation]
        test_chunks = []
        chsize = self.size * 2
        chlevel = self.level + 1
        if orientation == self.QTOP:
            test_chunk = self.centerX, self.centerY, self.centerZ - self.size
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[self.QTOP] = self.level
                    return self.level
            test_chunks.append(((self.centerX - self.size, self.centerY - self.size, \
                    self.centerZ - chsize), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY - self.size, \
                    self.centerZ - chsize), chsize, chlevel))
            test_chunks.append(((self.centerX - self.size, self.centerY + self.size, \
                    self.centerZ - chsize), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY + self.size, \
                    self.centerZ - chsize), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1
        if orientation == self.QLEFT:
            test_chunk = self.centerX - self.size, self.centerY, self.centerZ
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[orientation] = self.level
                    return self.level
            test_chunks.append(((self.centerX - chsize, self.centerY - self.size, \
                       self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX - chsize, self.centerY - self.size, \
                       self.centerZ + self.size), chsize, chlevel))
            test_chunks.append(((self.centerX - chsize, self.centerY + self.size, \
                       self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX - chsize, self.centerY + self.size, \
                       self.centerZ + self.size), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1
        if orientation == self.QRIGHT:
            test_chunk = self.centerX + self.size, self.centerY, self.centerZ
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[orientation] = self.level
                    return self.level
            test_chunks.append(((self.centerX + chsize, self.centerY - self.size, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + chsize, self.centerY - self.size, \
                        self.centerZ + self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + chsize, self.centerY + self.size, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + chsize, self.centerY + self.size, \
                        self.centerZ + self.size), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1
        if orientation == self.QFRONT:
            test_chunk = self.centerX, self.centerY - self.size, self.centerZ
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[orientation] = self.level
                    return self.level
            test_chunks.append(((self.centerX - self.size, self.centerY - chsize, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX - self.size, self.centerY - chsize, \
                        self.centerZ + self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY - chsize, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY - chsize, \
                        self.centerZ + self.size), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1
        if orientation == self.QBACK:
            test_chunk = self.centerX, self.centerY + self.size, self.centerZ
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[orientation] = self.level
                    return self.level
            test_chunks.append(((self.centerX - self.size, self.centerY + chsize, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX - self.size, self.centerY + chsize, \
                        self.centerZ + self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY + chsize, \
                        self.centerZ - self.size), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY + chsize, \
                        self.centerZ + self.size), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1
        if orientation == self.QBOTTOM:
            test_chunk = self.centerX, self.centerY, self.centerZ + self.size
            if test_chunk in self.status_chunks:
                if self.status_chunks[test_chunk]:
                    self.round_chunks[self.QTOP] = self.level
                    return self.level
            test_chunks.append(((self.centerX - self.size, self.centerY - self.size, \
                        self.centerZ + chsize), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY - self.size, \
                        self.centerZ + chsize), chsize, chlevel))
            test_chunks.append(((self.centerX - self.size, self.centerY + self.size, \
                        self.centerZ + chsize), chsize, chlevel))
            test_chunks.append(((self.centerX + self.size, self.centerY + self.size, \
                        self.centerZ + chsize), chsize, chlevel))
            for test_chunk in test_chunks:
                if test_chunk in self.status_chunks:
                    if self.status_chunks[test_chunk]:
                        self.round_chunks[orientation] = chlevel
                        return chlevel
            return self.level - 1


    def add_quad(self, n_vert, orientation, Force, x, y, dx, dy, Z, Z_minus, voxel):
        end = self.chunk_len - 1
        if orientation == self.QTOP:
            vert0 = Vec3(x, dy, Z)
            vert1 = Vec3(x, y, Z)
            vert2 = Vec3(dx, y, Z)
            vert3 = Vec3(dx, dy, Z)
            if not Force:
                voxel.block.top_tex = 'tech_top'
            u1, v1, u2, v2 = voxel.get_top_uv()
        elif orientation == self.QLEFT:
            vert0 = Vec3(x, y, Z_minus)
            vert1 = Vec3(x, y, Z)
            vert2 = Vec3(x, dy, Z)
            vert3 = Vec3(x, dy, Z_minus)
            if not Force:
                voxel.block.left_tex = 'tech_left'
            u1, v1, u2, v2 = voxel.get_left_uv()
        elif orientation == self.QRIGHT:
            vert0 = Vec3(dx, dy, Z_minus)
            vert1 = Vec3(dx, dy, Z)
            vert2 = Vec3(dx, y, Z)
            vert3 = Vec3(dx, y, Z_minus)
            if not Force:
                voxel.block.right_tex = 'tech_right'
            u1, v1, u2, v2 = voxel.get_right_uv()
        elif orientation == self.QFRONT:
            vert0 = Vec3(dx, y, Z_minus)
            vert1 = Vec3(dx, y, Z)
            vert2 = Vec3(x, y, Z)
            vert3 = Vec3(x, y, Z_minus)
            if not Force:
                voxel.block.front_tex = 'tech_front'
            u1, v1, u2, v2 = voxel.get_front_uv()
        elif orientation == self.QBACK:
            vert0 = Vec3(x, dy, Z_minus)
            vert1 = Vec3(x, dy, Z)
            vert2 = Vec3(dx, dy, Z)
            vert3 = Vec3(dx, dy, Z_minus)
            if not Force:
                voxel.block.back_tex = 'tech_back'
            u1, v1, u2, v2 = voxel.get_back_uv()
        elif orientation == self.QBOTTOM:
            vert0 = Vec3(dx, dy, Z_minus)
            vert1 = Vec3(dx, y, Z_minus)
            vert2 = Vec3(x, y, Z_minus)
            vert3 = Vec3(x, dy, Z_minus)
            if not Force:
                voxel.block.bottom_tex = 'tech_top'
            u1, v1, u2, v2 = voxel.get_bottom_uv()
        else:
            return

        self.vertex.addData3f(vert0)
        self.vertex.addData3f(vert1)
        self.vertex.addData3f(vert2)
        self.vertex.addData3f(vert3)

        norm1 = (vert0 - vert1).cross(vert0 - vert3)
        norm2 = (vert1 - vert2).cross(vert1 - vert3)

        self.normal.addData3f(norm1)
        self.normal.addData3f(norm1)
        self.normal.addData3f(norm1)
        self.normal.addData3f(norm2)


        self.texcoord.addData2f(v1, u1)
        self.texcoord.addData2f(v2, u1)
        self.texcoord.addData2f(v2, u2)
        self.texcoord.addData2f(v1, u2)

        self.tri.addConsecutiveVertices(0 + n_vert, 3)

        self.tri.addVertex(2 + n_vert)
        self.tri.addVertex(3 + n_vert)
        self.tri.addVertex(0 + n_vert)

    def check_empty(self, orientation, Force, X, Y, Z, X_plus, Y_plus, Z_plus, X_minus, Y_minus, Z_minus):
        if self.level > self.config.min_level and not Force:
            X_plus2, Y_plus2, Z_plus2, X_minus2, Y_minus2, Z_minus2 \
               = X_plus / 2, Y_plus / 2, Z_plus / 2, X_minus / 2, Y_minus / 2, Z_minus / 2
        if orientation == self.QSELF:
            return self.voxels[X, Y, Z].empty

        round_level = self.round_chunk_level(orientation)
        if orientation == self.QTOP:
            if Force or round_level == self.level:
                return self.voxels[X, Y, Z_plus].empty
            else:
                return True
                #if self.level > round_level:
                    #if self.voxels[X, Y, Z_plus].empty:
                        #return True
                    #if self.voxels[X_plus2, Y, Z_plus].empty:
                        #return True
                    #if self.voxels[X, Y_plus2, Z_plus].empty:
                        #return True
                    #if self.voxels[X_plus2, Y_plus2, Z_plus].empty:
                        #return True
                    #if self.voxels[X, Y, Z_plus2].empty:
                        #return True
                    #if self.voxels[X_plus2, Y, Z_plus2].empty:
                        #return True
                    #if self.voxels[X, Y_plus2, Z_plus2].empty:
                        #return True
                    #if self.voxels[X_plus2, Y_plus2, Z_plus2].empty:
                        #return True
                #else:
                    #if self.voxels[X, Y, Z_plus].empty:
                        #return True
                    #if self.voxels[X_plus, Y, Z_plus + self.size_voxel].empty:
                        #return True
        elif orientation == self.QLEFT:
            if self.level == round_level or Force:
                return self.voxels[X_minus, Y, Z].empty
            else:
                return True
                #if self.voxels[X_minus, Y, Z].empty:
                    #return True
                #if self.voxels[X_minus, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X_minus, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X_minus, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_minus2, Y, Z].empty:
                    #return True
                #if self.voxels[X_minus2, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X_minus2, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X_minus2, Y_plus2, Z_minus2].empty:
                    #return True
        elif orientation == self.QRIGHT:
            if self.level == round_level or Force:
                return self.voxels[X_plus, Y, Z].empty
            else:
                return True
                #if self.voxels[X_plus, Y, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X_plus, Y_plus2, Z_minus2].empty:
                    #return True
        elif orientation == self.QFRONT:
            if self.level == round_level or Force:
                return self.voxels[X, Y_minus, Z].empty
            else:
                return True
                #if self.voxels[X, Y_minus, Z].empty:
                    #return True
                #if self.voxels[X, Y_minus2, Z].empty:
                    #return True
                #if self.voxels[X, Y_minus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_minus2, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y_minus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X, Y_minus, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_minus, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y_minus, Z_minus2].empty:
                    #return True
        elif orientation == self.QBACK:
            if self.level == round_level or Force:
                return self.voxels[X, Y_plus, Z].empty
            else:
                return True
                #if self.voxels[X, Y_plus, Z].empty:
                    #return True
                #if self.voxels[X, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X, Y_plus, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus, Z].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus, Z_minus2].empty:
                    #return True
        elif orientation == self.QBOTTOM:
            if self.level == round_level or Force:
                return self.voxels[X, Y, Z_minus].empty
            else:
                return True
                #if self.voxels[X, Y, Z_minus].empty:
                    #return True
                #if self.voxels[X, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y, Z_minus2].empty:
                    #return True
                #if self.voxels[X, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z_minus2].empty:
                    #return True
                #if self.voxels[X_plus2, Y, Z_minus].empty:
                    #return True
                #if self.voxels[X, Y_plus2, Z_minus].empty:
                    #return True
                #if self.voxels[X_plus2, Y_plus2, Z_minus].empty:
                    #return True
        return False


    #@profile_decorator
    def create(self):
        self.chunk_geom = GeomNode('chunk_geom')

        self.vertex = GeomVertexWriter(self.v_data, 'vertex')
        self.normal = GeomVertexWriter(self.v_data, 'normal')
        self.texcoord = GeomVertexWriter(self.v_data, 'texcoord')

        # make buffer of vertices
        self.tri = GeomTriangles(Geom.UHStatic)


        end = self.chunk_len - 1
        n_vert = 0

        xX = {}
        yY = {}
        for i in xrange(-1, self.chunk_len + 1):
            xX[i] = self.start_x + (i * self.size_voxel)
            yY[i] = self.start_y + (i * self.size_voxel)

        for x in xrange(0, self.chunk_len):
            for y in xrange(0, self.chunk_len):
                X = xX[x]
                Y = yY[y]
                hZ = self.heights[X, Y]
                if self.end_z >= hZ >= self.start_z or self.dirt:
                    dx = x + 1
                    dy = y + 1
                    X_plus = xX[dx]
                    Y_plus = yY[dy]
                    X_minus = xX[x - 1]
                    Y_minus = yY[y - 1]
                    #if x == 0 or y == 0 or x == end or y == end or self.dirt:
                        #end_z = self.end_z
                    #else:
                    end_z = (hZ / self.size_voxel) * self.size_voxel
                    for Z in xrange(self.start_z, self.end_z + self.size_voxel, self.size_voxel):
                        if Z == end_z:
                            voxel = self.voxels[X, Y, hZ]
                        else:
                            voxel = self.voxels[X, Y, Z]
                        Z_minus = Z - self.size_voxel
                        Z_plus = Z + self.size_voxel
                        check_data = X, Y, Z, X_plus, Y_plus, Z_plus, X_minus, Y_minus, Z_minus
                        if self.check_empty(self.QSELF, False, *check_data) and Z != end_z:
                            continue
                        vert_data = x, y, dx, dy, Z, Z_minus, voxel

                        if Z == self.end_z:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QTOP, Force, *check_data):
                            self.add_quad(n_vert, self.QTOP, Force, *vert_data)
                            n_vert += 4

                        if x == 0:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QLEFT, Force, *check_data):
                            self.add_quad(n_vert, self.QLEFT, Force, *vert_data)
                            n_vert += 4

                        if y == 0:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QFRONT, Force, *check_data):
                            self.add_quad(n_vert, self.QFRONT, Force, *vert_data)
                            n_vert += 4

                        if x == end:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QRIGHT, Force, *check_data):
                            self.add_quad(n_vert, self.QRIGHT, Force, *vert_data)
                            n_vert += 4

                        if y == end:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QBACK, Force, *check_data):
                            self.add_quad(n_vert, self.QBACK, Force, *vert_data)
                            n_vert += 4

                        if Z == self.start_z:
                            Force = False
                        else:
                            Force = True
                        if self.check_empty(self.QBOTTOM, Force, *check_data):
                            self.add_quad(n_vert, self.QBOTTOM, Force, *vert_data)
                            n_vert += 4

        if n_vert > 0:
            self.chunk_np = self.attachNewNode('chunk_np')
            self.chunk_np.setTag('Chunk', '{0}'.format(self.chunk))
            self.geom = Geom(self.v_data)
            self.geom.addPrimitive(self.tri)
            self.chunk_geom.addGeom( self.geom )
            self.chunk_geom.setIntoCollideMask(BitMask32.bit(1))
            self.chunk_np.attachNewNode(self.chunk_geom)
            #self.chunk_np.setTwoSided(True)
            ts = TextureStage('ts')
            self.chunk_np.setTexture(ts, self.tex)
            self.chunk_np.setScale(self.size_voxel, self.size_voxel, 1)
            self.flattenStrong()
            return True
        else:
            return False

    def setX(self, DX):
        """Set to new X

        center X - self.size/2 - DX
        """
        x = self.start_x - DX
        NodePath.setX(self, x)

    def setY(self, DY):
        """Set to new Y

        center Y - self.size/2 - DY
        """
        y = self.start_y - DY
        NodePath.setY(self, y)


# vi: ft=python:tw=0:ts=4

