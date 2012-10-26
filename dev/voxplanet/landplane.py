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

    def show_forest(self, DX, DY, char_far, far, charpos, billboard = 1000):
        """Set to new X

        center X - self.size/2 - DX
        """

        tmp_node = NodePath('tmp')
        self.flatten_node.copyTo(tmp_node)
        tmp_node.reparentTo(self)
        self.flatten_node.removeNode()
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
            tmp_node.removeNode()
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
            tt = time.time()
            node.flattenStrong()
            print 'Flatten node: ', time.time() - tt
            time.sleep(self.config.tree_sleep)
            node.reparentTo(self.flatten_node)
            if added == count_trees:
                break

        print 'Added: ', added, time.time() - t

        t = time.time()
        self.flatten_node.flattenStrong()
        self.flatten_node.reparentTo(self)
        tmp_node.removeNode()
        print 'flatten all: ', time.time() - t


class ChunkModel(NodePath):
    """Chunk for quick render and create voxel-objects

    config - config of voxplanet
    heights - {(X, Y): height, (X2, Y2: height, ... (XN, YN): height}
    X, Y - center coordinates
    size - size of chunk (in scene coords)
    chunk_len - count of voxels
    tex_uv_height - function return of uv coordinates for height voxel
    tex - texture map
    """

    def __init__(self, world, config, heights, X, Y, size, chunk_len, tex_uv_height, tex):

        NodePath.__init__(self, 'ChunkModel')
        self.world = world
        self.X = X
        self.Y = Y
        self.Z = {}
        self.config = config
        self.heights = heights
        self.tex_uv_height = tex_uv_height
        self.tex = tex
        self.size = size
        self.chunk_len = chunk_len
        self.size_voxel = self.size / self.chunk_len
        if self.size_voxel <1:
            self.size_voxel = 1
        self.size2 = self.size / 2
        self.start_x = self.X - self.size2
        self.start_y = self.Y - self.size2

        self.chunk_geom = GeomNode('self.chunk_geom')
        self.v_format = GeomVertexFormat.getV3n3t2()
        self.v_data = GeomVertexData('chunk', self.v_format, Geom.UHStatic)

        vertex = GeomVertexWriter(self.v_data, 'vertex')
        normal = GeomVertexWriter(self.v_data, 'normal')
        texcoord = GeomVertexWriter(self.v_data, 'texcoord')

        # make buffer of vertices
        vertices = []
        n_vert = 0
        t = time.time()
        tri=GeomTriangles(Geom.UHStatic)

        def add_data(n_vert, v0, v1, v2, v3):
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

            heights = []
            heights.append(v0[2])
            heights.append(v1[2])
            heights.append(v2[2])
            heights.append(v3[2])
            maxh = max(heights)

            u1, v1, u2, v2 = self.tex_uv_height(maxh)

            texcoord.addData2f(u1, v2)
            texcoord.addData2f(u1, v1)
            texcoord.addData2f(u2, v1)
            texcoord.addData2f(u2, v2)

            tri.addConsecutiveVertices(0 + n_vert, 3)

            tri.addVertex(2 + n_vert)
            tri.addVertex(3 + n_vert)
            tri.addVertex(0 + n_vert)


        end = self.chunk_len - 1

        for x in xrange(0, self.chunk_len):
            for y in xrange(0, self.chunk_len):
                X = self.X - self.size2 + (x * self.size_voxel)
                Y = self.Y - self.size2 + (y * self.size_voxel)
                dX = X + self.size_voxel
                dY = Y + self.size_voxel

                dx = x + 1
                dy = y + 1

                v0 = Vec3(x, dy, self.heights[X, dY])
                v1 = Vec3(x, y, self.heights[X, Y])
                v2 = Vec3(dx, y, self.heights[dX, Y])
                v3 = Vec3(dx, dy, self.heights[dX, dY])

                add_data(n_vert, v0, v1, v2, v3)
                n_vert += 4

                if x == 0:
                    v0 = Vec3(x, y, self.heights[X, Y] - self.size_voxel)
                    v1 = Vec3(x, y, self.heights[X, Y])
                    v2 = Vec3(x, dy, self.heights[X, dY])
                    v3 = Vec3(x, dy, self.heights[X, dY] - self.size_voxel)
                    add_data(n_vert, v0, v1, v2, v3)
                    n_vert += 4

                if y == 0:
                    v0 = Vec3(dx, y, self.heights[dX, Y] - self.size_voxel)
                    v1 = Vec3(dx, y, self.heights[dX, Y])
                    v2 = Vec3(x, y, self.heights[X, Y])
                    v3 = Vec3(x, y, self.heights[X, Y] - self.size_voxel)
                    add_data(n_vert, v0, v1, v2, v3)
                    n_vert += 4

                if x == end:
                    v0 = Vec3(dx, dy, self.heights[dX, dY] - self.size_voxel)
                    v1 = Vec3(dx, dy, self.heights[dX, dY])
                    v2 = Vec3(dx, y, self.heights[dX, Y])
                    v3 = Vec3(dx, y, self.heights[dX, Y] - self.size_voxel)
                    add_data(n_vert, v0, v1, v2, v3)
                    n_vert += 4

                if y == end:
                    v0 = Vec3(x, dy, self.heights[X, dY] - self.size_voxel)
                    v1 = Vec3(x, dy, self.heights[X, dY])
                    v2 = Vec3(dx, dy, self.heights[dX, dY])
                    v3 = Vec3(dx, dy, self.heights[dX, dY] - self.size_voxel)
                    add_data(n_vert, v0, v1, v2, v3)
                    n_vert += 4

        self.geom = Geom(self.v_data)
        self.geom.addPrimitive(tri)
        self.chunk_geom.addGeom( self.geom )
        self.attachNewNode(self.chunk_geom)
        self.chunk_geom.setIntoCollideMask(BitMask32.bit(1))
        self.setTag('Chunk', 'Chunk: {0} {1} {2}'.format(self.X, self.Y, self.size))
        #self.setTwoSided(True)
        ts = TextureStage('ts')
        self.setTexture(ts, self.tex)
        self.setScale(self.size_voxel, self.size_voxel, 1)
        #t = time.time()
        # i love this function ^--^
        self.flattenStrong()
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

class LandNode():
    """Water / Land

    just square
    """
    def __init__(self, z, region):
        maker = CardMaker( 'land' )

        #self.landNP = render.attachNewNode(maker.generate())
        self.landNP = NodePath(maker.generate())
        self.landNP.reparentTo(render)
        self.landNP.setHpr(0,-90,0)
        self.landNP.setPos(-region, -region, z)
        self.landNP.setScale(region*3, 0, region*3)
        self.landNP.hide()
        self.landNP.setTransparency(TransparencyAttrib.MAlpha )

    def Destroy(self):
        self.landNP.removeNode()


    def hide(self):
        self.landNP.hide()

    def show(self):
        self.landNP.show()


# vi: ft=python:tw=0:ts=4

