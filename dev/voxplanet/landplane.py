#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Land classes - chunks, LandPlane, trees
"""

import random, time

from panda3d.core import Geom, GeomNode
from panda3d.core import GeomVertexData
from panda3d.core import Vec3, Vec2
from panda3d.core import VBase3, VBase2
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

class LowTreeModel(NodePath):
    """Cube-like tree
    """
    def __init__(self, name, size, body_tex = None, leaf_tex = None):
        NodePath.__init__(self, name)
        self.size = size
        self.body_tex = body_tex
        self.leaf_tex = leaf_tex
        self.make()
        self.flattenStrong()

    def make(self):
        self.body = CubeModel(*self.size)
        self.body.reparentTo(self)
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
        self.tree_nodes = {}
        self.bill_nodes = {}
        self.rbc = RBC('rbc')
        self.rbc_node = NodePath(self.rbc)
        #self.billboard_node = NodePath('billboard')
        #self.billboard_node.reparentTo(self)

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

    def show_forest(self, DX, DY, char_far, far, charpos, billboard = 1000):
        """Set to new X

        center X - self.size/2 - DX
        """

        tmp_node = NodePath('tmp')
        self.rbc_node.copyTo(tmp_node)
        tmp_node.reparentTo(self)
        self.rbc_node.detachNode()

        t = time.time()
        tex = self.world.trees[0].leaf_tex
        for tree_n in self.trees:
            # create or attach
            for coord in self.trees[tree_n]:
                #length_cam_2d = VBase2.length(Vec2(coord[0], coord[1]) - Vec2(charpos[0], charpos[1]))
                length_cam_3d = VBase3.length(Vec3(coord) - Vec3(charpos))

                if char_far >= length_cam_3d <= far:
                    if not self.tree_nodes.has_key(coord):
                        tree = self.world.trees[tree_n]
                        self.tree_nodes[coord] = self.attachNewNode('TreeNode')
                        tree.copyTo(self.tree_nodes[coord])
                    else:
                        if self.tree_nodes[coord].getParent() != self:
                            self.tree_nodes[coord].reparentTo(self)

                    x, y, z = coord
                    self.tree_nodes[coord].setPos(x - DX, y - DY, z-1)
                elif char_far >= length_cam_3d <= billboard:
                    height = self.world.trees[tree_n].size[2] / 2
                    height2 = height / 2
                    if not self.bill_nodes.has_key(coord):
                        maker = CardMaker( 'bill_tree' )
                        self.bill_nodes[coord] = NodePath(maker.generate())
                        self.bill_nodes[coord].reparentTo(self.rbc_node)
                        self.bill_nodes[coord].setTransparency(TransparencyAttrib.MAlpha)
                        self.bill_nodes[coord].setHpr(0,-90,0)
                        ts = TextureStage('ts')
                        self.bill_nodes[coord].setTexture(ts, tex)
                        self.bill_nodes[coord].setScale(height, 0, height)
                        self.bill_nodes[coord].setTexScale(ts, 10, 10)
                    else:
                        if self.bill_nodes[coord].getParent() != self.rbc_node:
                            self.bill_nodes[coord].reparentTo(self.rbc_node)

                    x, y, z = coord
                    self.bill_nodes[coord].setPos(x - DX - height2, y - DY - height2, z+height2)

                if length_cam_3d > far or length_cam_3d > char_far:
                    if self.tree_nodes.has_key(coord):
                        if self.tree_nodes[coord].getParent() == self:
                            self.tree_nodes[coord].detachNode()
                if length_cam_3d > billboard or length_cam_3d > char_far:
                    if self.bill_nodes.has_key(coord):
                        if self.bill_nodes[coord].getParent() == self.rbc_node:
                            self.bill_nodes[coord].detachNode()


        print 'Attach/detach trees loop: ', time.time() - t

        t = time.time()
        self.rbc.collect()
        self.rbc_node.reparentTo(self)
        tmp_node.removeNode()
        print 'collect: ', time.time() - t


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
    def __init__(self, config, heights, X, Y, size, chunk_len, tex_uv_height, tex):

        NodePath.__init__(self, 'ChunkModel')
        self.X = X
        self.Y = Y
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
        self.size_x = self.X + self.size2
        self.size_y = self.Y + self.size2

        chunk_geom = GeomNode('chunk_geom')

        sq_x = sq_y  = 0
        for x in xrange(self.start_x, self.size_x, self.size_voxel):
            sq_dx = sq_x + 1
            for y in xrange(self.start_y, self.size_y, self.size_voxel):
                dx = x + self.size_voxel
                dy = y + self.size_voxel
                z = self.heights[x, y]
                dz = z - (self.size_voxel)


                cube = []

                sq_dy = sq_y + 1

                heights = []
                heights.append(self.heights[x, y])
                heights.append(self.heights[x+self.size_voxel, y])
                heights.append(self.heights[x, y+self.size_voxel])
                heights.append(self.heights[x+self.size_voxel, y+self.size_voxel])
                maxh = max(heights)

                tex_coord = self.tex_uv_height(maxh)

                coord1 = Vec3(sq_x, sq_y, z)
                coord2 = Vec3(sq_dx, sq_y, self.heights[x+self.size_voxel, y])
                coord3 = Vec3(sq_dx, sq_dy, self.heights[x+self.size_voxel, y+self.size_voxel])
                coord4 = Vec3(sq_x, sq_dy, self.heights[x, y+self.size_voxel])

                chunk_geom.addGeom( make_square4v(coord1, coord2, coord3, coord4, tex_coord) )


                # skirt

                if x == self.start_x:
                    chunk_geom.addGeom( make_square4v(Vec3(sq_x, sq_y, z),
                                    Vec3(sq_x, sq_dy, self.heights[x, y + self.size_voxel]),
                                    Vec3(sq_x, sq_dy, self.heights[x, y + self.size_voxel]\
                                    - (self.size_voxel)),
                                    Vec3(sq_x, sq_y, dz),
                                    tex_coord) )
                elif dx == self.size_x:
                    chunk_geom.addGeom( make_square4v(Vec3(sq_dx, sq_y, self.heights[x +\
                                    self.size_voxel, y]),
                                    Vec3(sq_dx, sq_dy,
                                    self.heights[x + self.size_voxel, y + self.size_voxel]),
                                    Vec3(sq_dx, sq_dy, self.heights[x + self.size_voxel,\
                                    y + self.size_voxel] - (self.size_voxel)),
                                    Vec3(sq_dx, sq_y, self.heights[x + self.size_voxel, y]\
                                    - (self.size_voxel)),
                                    tex_coord) )

                if y == self.start_y:
                    chunk_geom.addGeom( make_square4v(Vec3(sq_x, sq_y, z),
                                    Vec3(sq_dx, sq_y, self.heights[x + self.size_voxel, y]),
                                    Vec3(sq_dx, sq_y,  self.heights[x + self.size_voxel, y]\
                                     - (self.size_voxel)),
                                    Vec3(sq_x, sq_y, dz),
                                    tex_coord) )
                elif dy == self.size_y:
                    chunk_geom.addGeom( make_square4v(Vec3(sq_x, sq_dy, self.heights[x, y +\
                                    self.size_voxel]),
                                    Vec3(sq_dx, sq_dy, self.heights[x + self.size_voxel,
                                     y + self.size_voxel]),
                                    Vec3(sq_dx, sq_dy, self.heights[x + self.size_voxel,\
                                     y + self.size_voxel] - (self.size_voxel)),
                                    Vec3(sq_x, sq_dy, self.heights[x, y + self.size_voxel]\
                                    - (self.size_voxel)),
                                    tex_coord) )

                sq_y += 1
            sq_x += 1
            sq_y = 0

        self.attachNewNode(chunk_geom)
        self.setTwoSided(True)
        ts = TextureStage('ts')
        self.setTexture(ts, self.tex)
        self.setScale(self.size_voxel, self.size_voxel, 1)
        self.flattenStrong()

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

