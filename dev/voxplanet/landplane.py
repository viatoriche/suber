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
        self.get_uv = self.block.get_uv

    def __call__(self):
        return self.empty

class Voxels(dict):
    def __init__(self, heights, get_coord_block):
        self.heights = heights
        self.get_coord_block = get_coord_block
        self.repaint = []

    def __setitem__(self, key, voxel):
        if self.has_key(key):
            if item not in self.repaint:
                self.repaint.append(key)
        dict.__setitem__(self, key, voxel)

    def check_repaint(self, chunk):
        center, size, level = chunk
        # TODO: check chunk for repaint
        return False

    def __getitem__(self, item):
        if self.has_key(item):
            return dict.__getitem__(self, item)
        else:
            empty = self.heights.check_empty(item)
            block = self.get_coord_block(item)
            vox = Voxel(empty, block)
            self[item] = vox
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


    def __init__(self, config, heights, voxels, chunk, tex, water_tex, dirt = False):
        NodePath.__init__(self, 'ChunkModel')
        self.dirt = dirt
        self.config = config
        self.heights = heights
        self.voxels = voxels
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

        self.level_3d = self.config.level_3d


        self.v_format = GeomVertexFormat.getV3n3t2()
        self.v_data = GeomVertexData('chunk', self.v_format, Geom.UHStatic)

        if self.centerZ == 0:
            self.water = WaterNode(0, 0, self.size, self.water_tex)
            self.water.setTwoSided(True)
            self.water.reparentTo(self)

        self.end_z = self.start_z + self.size
        if not self.dirt:
            inchunk = False
            for X in xrange(self.start_x, self.start_x + self.size, self.size_voxel):
                for Y in xrange(self.start_y, self.start_y + self.size, self.size_voxel):
                    h0 = self.heights[X, Y]
                    h1 = self.heights[X+self.size_voxel, Y]
                    h2 = self.heights[X, Y+self.size_voxel]
                    h3 = self.heights[X+self.size_voxel, Y+self.size_voxel]
                    h = min([h0, h1, h2, h3])
                    if h >= self.start_z and h < self.start_z + self.size:
                        inchunk = True
                        break
                if inchunk:
                    break

            if inchunk:
                self.create()
        else:
            self.create()

        self.flattenStrong()


    #@profile_decorator
    def create(self):
        self.chunk_geom = GeomNode('chunk_geom')

        vertex = GeomVertexWriter(self.v_data, 'vertex')
        normal = GeomVertexWriter(self.v_data, 'normal')
        texcoord = GeomVertexWriter(self.v_data, 'texcoord')

        # make buffer of vertices
        vertices = []
        tri=GeomTriangles(Geom.UHStatic)

        def add_data(n_vert, v0, v1, v2, v3, voxel):
            vertex.addData3f(v0)
            vertex.addData3f(v1)
            vertex.addData3f(v2)
            vertex.addData3f(v3)

            side1 = v0 - v1
            side2 = v0 - v3
            norm1 = side1.cross(side2)
            side1 = v1 - v2
            side2 = v1 - v3
            norm2 = side1.cross(side2)

            normal.addData3f(norm1)
            normal.addData3f(norm1)
            normal.addData3f(norm1)
            normal.addData3f(norm2)

            u1, v1, u2, v2 = voxel.get_uv()

            texcoord.addData2f(v1, u1)
            texcoord.addData2f(v2, u1)
            texcoord.addData2f(v2, u2)
            texcoord.addData2f(v1, u2)

            tri.addConsecutiveVertices(0 + n_vert, 3)

            tri.addVertex(2 + n_vert)
            tri.addVertex(3 + n_vert)
            tri.addVertex(0 + n_vert)


        #def deep_z(X, Y, Z, min_z, n_vert):
            #for z in xrange(Z, min_z, -self.size_voxel):

                #if self.voxels[X, Y, z].empty:
                    #continue

                #if self.voxels[X, Y, z+self.size_voxel].empty:
                    #v0 = Vec3(x, dy, z)
                    #v1 = Vec3(x, y, z)
                    #v2 = Vec3(dx, y, z)
                    #v3 = Vec3(dx, dy, z)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z])
                    #n_vert += 4

                #if self.voxels[X+self.size_voxel, Y, z].empty:
                    #v0 = Vec3(dx, dy, z - self.size_voxel)
                    #v1 = Vec3(dx, dy, z)
                    #v2 = Vec3(dx, y, z)
                    #v3 = Vec3(dx, y, z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z])
                    #n_vert += 4

                #if self.voxels[X-self.size_voxel, Y, z].empty:
                    #v0 = Vec3(x, y, z - self.size_voxel)
                    #v1 = Vec3(x, y, z)
                    #v2 = Vec3(x, dy, z)
                    #v3 = Vec3(x, dy, z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z])
                    #n_vert += 4

                #if self.voxels[X, Y+self.size_voxel, z].empty:
                    #v0 = Vec3(x, dy, z - self.size_voxel)
                    #v1 = Vec3(x, dy, z)
                    #v2 = Vec3(dx, dy, z)
                    #v3 = Vec3(dx, dy, z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z])
                    #n_vert += 4

                #if self.voxels[X, Y-self.size_voxel, z].empty:
                    #v0 = Vec3(dx, y, z - self.size_voxel)
                    #v1 = Vec3(dx, y, z)
                    #v2 = Vec3(x, y, z)
                    #v3 = Vec3(x, y, z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z])
                    #n_vert += 4

                #if self.voxels[X, Y, z-self.size_voxel].empty:
                    #v0 = Vec3(dx, dy, z-self.size_voxel)
                    #v1 = Vec3(dx, y, z-self.size_voxel)
                    #v2 = Vec3(x, y, z-self.size_voxel)
                    #v3 = Vec3(x, dy, z-self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, z-self.size_voxel])
                    #n_vert += 4

            #return n_vert

        def add_top_net_quad(n_vert, data):
            x, y, dx, dy, X, Y, dX, dY, Z = data
            v0 = Vec3(x, dy, self.heights[X, dY])
            v1 = Vec3(x, y, self.heights[X, Y])
            v2 = Vec3(dx, y, self.heights[dX, Y])
            v3 = Vec3(dx, dy, self.heights[dX, dY])
            add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z])
            return n_vert + 4

        def add_left_skirt(n_vert, data):
            x, y, dx, dy, X, Y, dX, dY, Z = data
            v0 = Vec3(x, y, self.heights[X, Y] - self.size_voxel)
            v1 = Vec3(x, y, self.heights[X, Y])
            v2 = Vec3(x, dy, self.heights[X, dY])
            v3 = Vec3(x, dy, self.heights[X, dY] - self.size_voxel)
            add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, self.heights[X, Y]])
            return n_vert + 4

        def add_front_skirt(n_vert, data):
            x, y, dx, dy, X, Y, dX, dY, Z = data
            v0 = Vec3(dx, y, self.heights[dX, Y] - self.size_voxel)
            v1 = Vec3(dx, y, self.heights[dX, Y])
            v2 = Vec3(x, y, self.heights[X, Y])
            v3 = Vec3(x, y, self.heights[X, Y] - self.size_voxel)
            add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, self.heights[X, Y]])
            return n_vert + 4

        def add_right_skirt(n_vert, data):
            x, y, dx, dy, X, Y, dX, dY, Z = data
            v0 = Vec3(dx, dy, self.heights[dX, dY] - self.size_voxel)
            v1 = Vec3(dx, dy, self.heights[dX, dY])
            v2 = Vec3(dx, y, self.heights[dX, Y])
            v3 = Vec3(dx, y, self.heights[dX, Y] - self.size_voxel)
            add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, self.heights[X, Y]])
            return n_vert + 4

        def add_back_skirt(n_vert, data):
            x, y, dx, dy, X, Y, dX, dY, Z = data
            v0 = Vec3(x, dy, self.heights[X, dY] - self.size_voxel)
            v1 = Vec3(x, dy, self.heights[X, dY])
            v2 = Vec3(dx, dy, self.heights[dX, dY])
            v3 = Vec3(dx, dy, self.heights[dX, dY] - self.size_voxel)
            add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, self.heights[X, Y]])
            return n_vert + 4


        end = self.chunk_len - 1
        #t = time.time()
        def add_current_verts(n_vert, x, y, xX, yY, Z):
            X = xX[x]
            Y = yY[y]
            dx = x + 1
            dy = y + 1

            dX = xX[dx]
            dY = yY[dy]

            landZ = self.heights[X, Y]

            if Z == None:
                Z = landZ

            all_verts_data = x, y, dx, dy, X, Y, dX, dY, Z

            if self.level > self.level_3d:

                n_vert = add_top_net_quad(n_vert, all_verts_data)

                if x == 0:
                    n_vert = add_left_skirt(n_vert, all_verts_data)

                if y == 0:
                    n_vert = add_front_skirt(n_vert, all_verts_data)

                if x == end:
                    n_vert = add_right_skirt(n_vert, all_verts_data)

                if y == end:
                    n_vert = add_back_skirt(n_vert, all_verts_data)

            #else:

                #if self.voxels[X+self.size_voxel, Y, Z].empty:
                    #v0 = Vec3(dx, dy, Z - self.size_voxel)
                    #v1 = Vec3(dx, dy, self.heights[dX, dY])
                    #v2 = Vec3(dx, y, self.heights[dX, Y])
                    #v3 = Vec3(dx, y, Z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z])
                    #n_vert += 4

                #if self.voxels[X-self.size_voxel, Y, Z].empty:
                    #v0 = Vec3(x, y, Z - self.size_voxel)
                    #v1 = Vec3(x, y, self.heights[X, Y])
                    #v2 = Vec3(x, dy, self.heights[X, dY])
                    #v3 = Vec3(x, dy, Z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z])
                    #n_vert += 4

                #if self.voxels[X, Y+self.size_voxel, Z].empty:
                    #v0 = Vec3(x, dy, Z - self.size_voxel)
                    #v1 = Vec3(x, dy, self.heights[X, dY])
                    #v2 = Vec3(dx, dy, self.heights[dX, dY])
                    #v3 = Vec3(dx, dy, Z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z])
                    #n_vert += 4

                #if self.voxels[X, Y-self.size_voxel, Z].empty:
                    #v0 = Vec3(dx, y, Z - self.size_voxel)
                    #v1 = Vec3(dx, y, self.heights[dX, Y])
                    #v2 = Vec3(x, y, self.heights[X, Y])
                    #v3 = Vec3(x, y, Z - self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z])
                    #n_vert += 4

                #if self.voxels[X, Y, Z-self.size_voxel].empty:
                    #v0 = Vec3(dx, dy, Z-self.size_voxel)
                    #v1 = Vec3(dx, y, Z-self.size_voxel)
                    #v2 = Vec3(x, y, Z-self.size_voxel)
                    #v3 = Vec3(x, dy, Z-self.size_voxel)
                    #add_data(n_vert, v0, v1, v2, v3, self.voxels[X, Y, Z-self.size_voxel])
                    #n_vert += 4
            return n_vert

        def add_all_verts(chunk_len):
            n_vert = 0

            xX = {}
            yY = {}
            for i in xrange(0, chunk_len + 1):
                xX[i] = self.start_x + (i * self.size_voxel)
                yY[i] = self.start_y + (i * self.size_voxel)

            if self.level > self.level_3d:
                for x in xrange(0, chunk_len):
                    for y in xrange(0, chunk_len):
                        n_vert = add_current_verts(n_vert, x, y, xX, yY, Z = None)

            else:
                for Z in xrange(self.start_z, self.end_z, self.size_voxel):
                    for x in xrange(0, chunk_len):
                        for y in xrange(0, chunk_len):
                            n_vert = add_current_verts(n_vert, x, y, xX, yY, Z)
            return n_vert

        n_vert = add_all_verts(self.chunk_len)
        self.chunk_np = self.attachNewNode('chunk_np')
        self.chunk_np.setTag('Chunk', '{0}'.format(self.chunk))
        self.geom = Geom(self.v_data)
        self.geom.addPrimitive(tri)
        self.chunk_geom.addGeom( self.geom )
        self.chunk_geom.setIntoCollideMask(BitMask32.bit(1))
        self.chunk_np.attachNewNode(self.chunk_geom)
        #self.chunk_np.setTwoSided(True)
        ts = TextureStage('ts')
        self.chunk_np.setTexture(ts, self.tex)
        self.chunk_np.setScale(self.size_voxel, self.size_voxel, 1)
        #t = time.time()
        # i love this function ^--^
        #print 'flatten chunk: ', time.time() - t

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

