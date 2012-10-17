#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Land classes - chunks, LandPlane, trees
"""

import random, time

from panda3d.core import Geom, GeomNode
from panda3d.core import GeomVertexData
from panda3d.core import Vec3, Vec2
from panda3d.core import VBase3
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


class TreeModel(NodePath):

    def __init__(self, length, tex, leafModel, leafTex,
                 pos=Vec3(0, 0, 0), numIterations = 11,
                 numCopies = 6, vecList=[Vec3(0,0,1),
                 Vec3(1,0,0), Vec3(0,-1,0)]):

        NodePath.__init__(self, 'Tree')

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

class ForestNode(NodePath):

    def __init__(self, config, world):
        NodePath.__init__(self, 'ForestNode')
        self.config = config
        self.world = world
        self.trees = {}
        self.rbc = RBC('rbc')
        self.rbc_node = NodePath(self.rbc)
        self.rbc_node.reparentTo(self)
        self.tree_nodes = {}

    def add_trees(self, chunk):
        # level
        sx = chunk.start_x
        sy = chunk.start_y
        ex = chunk.size_x
        ey = chunk.size_y

        t = time.time()
        trees = self.world.treeland[sx, sy, ex, ey]
        for tree in trees:
            if not self.trees.has_key(tree):
                self.trees[tree] = []
            self.trees[tree] = self.trees[tree] + trees[tree]

    def show_forest(self, DX, DY, far, charpos):
        """Set to new X

        center X - self.size/2 - DX
        """

        collect = False

        for tree_n in self.trees:
            # create or attach
            for coord in self.trees[tree_n]:
                length_cam = VBase3.length(Vec3(coord) - Vec3(charpos))

                if length_cam <= far:

                    if not self.tree_nodes.has_key(coord):
                        tree = self.world.trees[tree_n]
                        self.tree_nodes[coord] = self.rbc_node.attachNewNode('TreeNode')
                        tree.copyTo(self.tree_nodes[coord])
                        collect = True
                    else:
                        if self.tree_nodes[coord].getParent() != self.rbc_node:
                            self.tree_nodes[coord].reparentTo(self.rbc_node)
                            collect = True

                    x, y, z = coord
                    self.tree_nodes[coord].setPos(x - DX, y - DY, z-1)

                else:
                    if self.tree_nodes.has_key(coord):
                        if self.tree_nodes[coord].getParent() == self.rbc_node:
                            self.tree_nodes[coord].detachNode()
                            collect = True



        if collect:
            self.rbc.collect()


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
        self.Z = {}

        for x in xrange(self.start_x-self.size_voxel, self.size_x+\
                            self.size_voxel, self.size_voxel):
            for y in xrange(self.start_y-self.size_voxel, self.size_y\
                            +self.size_voxel, self.size_voxel):
                self.Z[x, y] = self.heights[x, y]

        self.create()

    def create(self):
        """create chunk

        """
        cubes = []
        sq_x = sq_y  = 0
        for x in xrange(self.start_x, self.size_x, self.size_voxel):
            sq_dx = sq_x + 1
            for y in xrange(self.start_y, self.size_y, self.size_voxel):
                dx = x + self.size_voxel
                dy = y + self.size_voxel
                z = self.Z[x, y]
                dz = z - (self.size_voxel)


                cube = []

                sq_dy = sq_y + 1
                #sq_x = x
                #sq_y = y
                #sq_dx = dx
                #sq_dy = dy

                heights = []
                heights.append(self.Z[x, y])
                heights.append(self.Z[x+self.size_voxel, y])
                heights.append(self.Z[x, y+self.size_voxel])
                heights.append(self.Z[x+self.size_voxel, y+self.size_voxel])
                maxh = max(heights)

                #if self.size_voxel <= 4:
                    #if maxh <= self.config.land_mount_level[1]:
                        #if random.randint(1,20) == 20:
                            #tree = NodePath('ChunkTree')
                            #self.trees[random.randint(0, self.config.tree_models - 1)].copyTo(tree)
                            #tree.reparentTo(self)
                            #tree.setPos(sq_x, sq_y, maxh)

                tex_coord = self.tex_uv_height(maxh)

                coord1 = sq_x, sq_y, z
                coord2 = sq_dx, sq_y, self.Z[x+self.size_voxel, y]
                coord3 = sq_dx, sq_dy, self.Z[x+self.size_voxel, y+self.size_voxel]
                coord4 = sq_x, sq_dy, self.Z[x, y+self.size_voxel]

                cube.append( make_square4v(coord1, coord2, coord3, coord4, tex_coord) )


                # skirt

                if x == self.start_x:
                    cube.append( make_square4v((sq_x, sq_y, z),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]\
                                    - (self.size_voxel)),
                                    (sq_x, sq_y, dz),
                                    tex_coord) )
                if dx == self.size_x:
                    cube.append( make_square4v((sq_dx, sq_y, self.Z[x +\
                                    self.size_voxel, y]),
                                    (sq_dx, sq_dy,
                                    self.Z[x + self.size_voxel, y + self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,\
                                    y + self.size_voxel] - (self.size_voxel)),
                                    (sq_dx, sq_y, self.Z[x + self.size_voxel, y]\
                                    - (self.size_voxel)),
                                    tex_coord) )

                if y == self.start_y:
                    cube.append( make_square4v((sq_x, sq_y, z),
                                    (sq_dx, sq_y, self.Z[x + self.size_voxel, y]),
                                    (sq_dx, sq_y,  self.Z[x + self.size_voxel, y]\
                                     - (self.size_voxel)),
                                    (sq_x, sq_y, dz),
                                    tex_coord) )
                if dy == self.size_y:
                    cube.append( make_square4v((sq_x, sq_dy, self.Z[x, y +\
                                    self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,
                                     y + self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,\
                                     y + self.size_voxel] - (self.size_voxel)),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]\
                                    - (self.size_voxel)),
                                    tex_coord) )

                #if z > self.Z[x - self.size_voxel, y]:
                    #cube.append( makeSquare(sq_x, sq_y, z,    sq_x, sq_dy, dz,  tex_coord) )
                #if z > self.Z[x + self.size_voxel, y]:
                    #cube.append( makeSquare(sq_dx, sq_y, z,    sq_dx, sq_dy, dz,  tex_coord) )

                #if z > self.Z[x, y - self.size_voxel]:
                    #cube.append( makeSquare(sq_x, sq_y, z,    sq_dx, sq_y, dz,  tex_coord) )
                #if z > self.Z[x, y + self.size_voxel]:
                    #cube.append( makeSquare(sq_x, sq_dy, z,    sq_dx, sq_dy, dz,  tex_coord) )


                cubes.append(cube)


                #if self.level >= self.config.tree_level:
                    #if sq_x % 4 == 0 and sq_y % 4 == 0:
                        #tree = self.treeland[x, y, z]
                        #if tree != None:
                            #placetree = self.attachNewNode("Tree")
                            #placetree.setPos(sq_x, sq_y, z-1)
                            #print 'Tree: ', x, y, z-1, ' -> ', sq_x, sq_y, z-1
                            #tree.instanceTo(placetree)
                sq_y += 1
            sq_x += 1
            sq_y = 0

        chunk_geom = GeomNode('chunk_geom')
        for cube in cubes:
            for square in cube:
                chunk_geom.addGeom(square)

        self.attachNewNode(chunk_geom)
        self.setTwoSided(True)
        ts = TextureStage('ts')
        self.setTexture(ts, self.tex)
        self.setScale(self.size_voxel, self.size_voxel, 1)
        #self.flattenMedium()
        self.flattenStrong()
        #self.flattenLight()
        #self.setX(self.DX)
        #self.setY(self.DY)

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

