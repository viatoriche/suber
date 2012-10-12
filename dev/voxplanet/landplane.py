#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
land plane
"""

import random

from panda3d.core import Geom, GeomNode
from panda3d.core import GeomVertexData
from panda3d.core import Vec3
from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import TextureStage
from pandac.PandaModules import TransparencyAttrib
from voxplanet.support import makeSquare_net, drawBody, drawLeaf, treeform
from voxplanet.support import pstat

class TreeModel(NodePath):

    def __init__(self, length, tex, leafModel, pos=Vec3(0, 0, 0), numIterations = 11, numCopies = 4, vecList=[Vec3(0,0,1),
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
        self.make()
        self.setTexture(self.tex, 1)

    def make(self):

        if self.numIterations > 0:

            drawBody(self, self.bodydata, self.pos,
                     self.vecList, self.length.getX())


            #move foward along the right axis
            newPos=self.pos + self.vecList[0] * self.length.length()


            #only branch every third level (sorta)
            if self.numIterations % 3 == 0:
                #decrease dimensions when we branch
                self.length = Vec3(self.length.getX() / 2, self.length.getY() / 2,
                              self.length.getZ() / 1.1)
                for i in range(self.numCopies):
                    self.numIterations =- 1
                    self.make()
            else:
                #just make another branch connected to this one with a small variation in direction
                self.numIterations =- 1
                self.make()

        else:
            drawBody(self, self.bodydata, self.pos, self.vecList, self.length.getX(), False)
            drawLeaf(self, self.bodydata, self.leafModel, self.pos, self.vecList)

class ChunkModel(NodePath):
    """Chunk for quick render and create cube-objects

    world - link to world object
    X, Y = start coordinates
    """
    def __init__(self, config, heights, X, Y, size, chunk_len, tex_uv_height, tex):
        """
        heights = dict of heights for coordinates
        X, Y - center of chunk
        size - size of chunk (in scene coords)
        chunk_len - count of voxels
        tex_uv_height - function return of uv coordinates for height voxel
        tex - texture map
        """

        NodePath.__init__(self, 'ChunkModel_{0}-{1}_{2}'.format(X, Y, size))
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

                cube.append( makeSquare_net(coord1, coord2, coord3, coord4, tex_coord) )


                # skirt

                if x == self.start_x:
                    cube.append( makeSquare_net((sq_x, sq_y, z),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]\
                                    - (self.size_voxel*10)),
                                    (sq_x, sq_y, dz),
                                    tex_coord) )
                if dx == self.size_x:
                    cube.append( makeSquare_net((sq_dx, sq_y, self.Z[x +\
                                    self.size_voxel, y]),
                                    (sq_dx, sq_dy,
                                    self.Z[x + self.size_voxel, y + self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,\
                                    y + self.size_voxel] - (self.size_voxel*10)),
                                    (sq_dx, sq_y, self.Z[x + self.size_voxel, y]\
                                    - (self.size_voxel*10)),
                                    tex_coord) )

                if y == self.start_y:
                    cube.append( makeSquare_net((sq_x, sq_y, z),
                                    (sq_dx, sq_y, self.Z[x + self.size_voxel, y]),
                                    (sq_dx, sq_y,  self.Z[x + self.size_voxel, y]\
                                     - (self.size_voxel*10)),
                                    (sq_x, sq_y, dz),
                                    tex_coord) )
                if dy == self.size_y:
                    cube.append( makeSquare_net((sq_x, sq_dy, self.Z[x, y +\
                                    self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,
                                     y + self.size_voxel]),
                                    (sq_dx, sq_dy, self.Z[x + self.size_voxel,\
                                     y + self.size_voxel] - (self.size_voxel*10)),
                                    (sq_x, sq_dy, self.Z[x, y + self.size_voxel]\
                                    - (self.size_voxel*10)),
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

