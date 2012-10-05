#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
land plane
"""

import time
from config import Config
from panda3d.core import CardMaker
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import NodePath
from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import TransparencyAttrib

class ChunkModel(NodePath):
    """Chunk for quick render and create cube-objects

    world - link to world object
    X, Y = start coordinates
    """
    def __init__(self, world, X, Y, size):
        NodePath.__init__(self, 'ChunkModel_{0}-{1}_{2}'.format(X, Y, size))
        self.world = world
        self.X = X
        self.Y = Y
        self.size = size
        self.create()
        #return self.create()

    def create(self):
        """create chunk

        """
        form = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('chunk_{0}-{1}_{2}'.format(self.X, self.Y, self.size),
                               form, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        #normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        tris = []
        j = 0
        t = time.time()
        size_voxel = self.size / 16
        #print 'CHUNK MODEL INIT: ',self.X, self.Y, self.size,\
              #'\n\t\tvoxel size: ', size_voxel,\
              #'\n\t\tstart X, Y: ', self.X - (self.size / 2), self.Y - (self.size / 2)

        for x in xrange(self.X - (self.size / 2), self.X + (self.size / 2), size_voxel):
            for y in xrange(self.Y - (self.size / 2), self.Y + (self.size / 2), size_voxel):
                #z = self.world.map_3d[x, y]
                z = 0
                #print '\t\t\t\t X, Y: ',x, y
                vertex.addData3f(x, y, z)
                vertex.addData3f(x + size_voxel, y, z)
                vertex.addData3f(x + size_voxel, y+size_voxel, z)
                vertex.addData3f(x, y+size_voxel, z)
                #print '\t\t\tvertexes: 1 - ',x, y, z, ' | 2 - ', x+size_voxel, y, z, ' | 3 - ', x + size_voxel, y + size_voxel, z, ' | 4 - ', x, y+size_voxel, z

                tri1=GeomTriangles(Geom.UHDynamic)
                tri1.addVertex(j)
                tri1.addVertex(j+1)
                tri1.addVertex(j+3)

                tri2=GeomTriangles(Geom.UHDynamic)
                tri2.addConsecutiveVertices(j+1, 3)
                j += 4

                tris.append(tri1)
                tris.append(tri2)

                color.addData4f(1.0, 0.0, 0.0, 1.0)
                color.addData4f(0.0, 1.0, 0.0, 1.0)
                color.addData4f(0.0, 0.0, 1.0, 1.0)
                color.addData4f(1.0, 0.0, 1.0, 1.0)

        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        texcoord.addData2f(1.0, 1.0)

        chunk_data = Geom(vdata)
        for tri in tris:
            chunk_data.addPrimitive(tri)

        geom_node = GeomNode('chunk_node_{0}_{1}_{2}'.format(self.X, self.Y, self.size))
        geom_node.addGeom(chunk_data)
        nodePath = self.attachNewNode(geom_node)
        return nodePath

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

