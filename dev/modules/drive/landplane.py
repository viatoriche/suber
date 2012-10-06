#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
land plane
"""

from config import Config
from modules.drive.textures import textures
from panda3d.core import CardMaker
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Vec3
from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import TextureStage
from pandac.PandaModules import TransparencyAttrib

#you cant normalize in-place so this is a helper function
def myNormalize(myVec):
    myVec.normalize()
    return myVec

#helper function to make a square given the Lower-Left-Hand and Upper-Right-Hand corners
def makeSquare(x1,y1,z1, x2,y2,z2, tex_coord):
    format=GeomVertexFormat.getV3n3t2()
    vdata=GeomVertexData('square', format, Geom.UHStatic)

    vertex=GeomVertexWriter(vdata, 'vertex')
    normal=GeomVertexWriter(vdata, 'normal')
    texcoord=GeomVertexWriter(vdata, 'texcoord')

    #make sure we draw the sqaure in the right plane
    if x1!=x2:
        vertex.addData3f(x1, y1, z1)
        vertex.addData3f(x2, y1, z1)
        vertex.addData3f(x2, y2, z2)
        vertex.addData3f(x1, y2, z2)

        normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
        normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y1-1, 2*z1-1)))
        normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
        normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y2-1, 2*z2-1)))

    else:
        vertex.addData3f(x1, y1, z1)
        vertex.addData3f(x2, y2, z1)
        vertex.addData3f(x2, y2, z2)
        vertex.addData3f(x1, y1, z2)

        normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
        normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z1-1)))
        normal.addData3f(myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
        normal.addData3f(myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z2-1)))

    #adding different colors to the vertex for visibility

    u1, v1, u2, v2 = tex_coord

    texcoord.addData2f(u1, v2)
    texcoord.addData2f(u1, v1)
    texcoord.addData2f(u2, v1)
    texcoord.addData2f(u2, v2)

    #quads arent directly supported by the Geom interface
    #you might be interested in the CardMaker class if you are
    #interested in rectangle though
    tri1=GeomTriangles(Geom.UHStatic)
    tri2=GeomTriangles(Geom.UHStatic)

    tri1.addVertex(0)
    tri1.addVertex(1)
    tri1.addVertex(3)

    tri2.addConsecutiveVertices(1,3)

    tri1.closePrimitive()
    tri2.closePrimitive()

    square=Geom(vdata)
    square.addPrimitive(tri1)
    square.addPrimitive(tri2)

    return square

class ChunkModel(NodePath):
    """Chunk for quick render and create cube-objects

    world - link to world object
    X, Y = start coordinates
    """
    config = Config()
    def __init__(self, world, X, Y, size, chunk_len):
        NodePath.__init__(self, 'ChunkModel_{0}-{1}_{2}'.format(X, Y, size))
        self.world = world
        self.X = X
        self.Y = Y
        self.size = size
        self.chunk_len = chunk_len
        self.create()
        #return self.create()

    def create(self):
        """create chunk

        """
        cubes = []
        size_voxel = self.size / self.chunk_len
        size2 = self.size / 2
        start_x = self.X - size2
        start_y = self.Y - size2
        size_x = self.X + size2
        size_y = self.Y + size2
        Z = {}

        for x in xrange(start_x-size_voxel, size_x+size_voxel, size_voxel):
            for y in xrange(start_y-size_voxel, size_y+size_voxel, size_voxel):
                Z[x, y] = self.world.map_3d[x, y]

        for x in xrange(start_x, size_x, size_voxel):
            for y in xrange(start_y, size_y, size_voxel):
                dx = x + size_voxel
                dy = y + size_voxel
                z = Z[x, y]
                dz = z - (size_voxel * 10)

                cube = []

                tex_coord = textures.get_block_uv_height(z)

                cube.append( makeSquare(x, y, z,    dx, dy, z,  tex_coord) )

                if z > Z[x - size_voxel, y]:
                    cube.append( makeSquare(x, y, z,    x, dy, dz,  tex_coord) )
                if z > Z[x + size_voxel, y]:
                    cube.append( makeSquare(dx, y, z,    dx, dy, dz,  tex_coord) )

                if z > Z[x, y - size_voxel]:
                    cube.append( makeSquare(x, y, z,    dx, y, dz,  tex_coord) )
                if z > Z[x, y + size_voxel]:
                    cube.append( makeSquare(x, dy, z,    dx, dy, dz,  tex_coord) )


                cubes.append(cube)

        chunk_geom = GeomNode('chunk_geom')
        for cube in cubes:
            for square in cube:
                chunk_geom.addGeom(square)

        self.attachNewNode(chunk_geom)
        self.setTwoSided(True)
        ts = TextureStage('ts')
        self.setTexture(ts, textures['world_blocks'])
        self.setTexScale(ts, 1, 1)

class LandNode():
    """Water / Land
    """
    config = Config()
    def __init__(self, z):
        maker = CardMaker( 'land' )

        #self.landNP = render.attachNewNode(maker.generate())
        self.landNP = NodePath(maker.generate())
        self.landNP.reparentTo(render)
        self.landNP.setHpr(0,-90,0)
        self.landNP.setPos(0,0,z)
        self.landNP.setScale(16777216, 0, 16777216)
        self.landNP.hide()
        self.landNP.setTransparency(TransparencyAttrib.MAlpha )

    def Destroy(self):
        self.landNP.removeNode()


    def hide(self):
        self.landNP.hide()

    def show(self):
        self.landNP.show()


# vi: ft=python:tw=0:ts=4

