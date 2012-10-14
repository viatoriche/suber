#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Support functions for generate models and other

Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
"""

import cProfile
import math, random

from panda3d.core import Geom, GeomTrifans, GeomTristrips
from panda3d.core import GeomTriangles, GeomVertexWriter
from panda3d.core import GeomVertexData
from panda3d.core import GeomVertexFormat
from panda3d.core import PStatCollector
from panda3d.core import Vec3

class BCol():
    """Class collector for pstat
    """
    custom_collectors = {}

b_collector = BCol()

def profile_decorator(func):
    """Decorator for cProfile
    """
    cprofile = cProfile.Profile()
    def do_profile(*args, **kargs):
        cprofile.clear()
        returned = cprofile.runcall(func, *args, **kargs)
        cprofile.create_stats()
        cprofile.print_stats(sort = 1)
        return returned
    do_profile.__name__ = func.__name__
    do_profile.__dict__ = func.__dict__
    do_profile.__doc__ = func.__doc__
    return do_profile

def pstat(func):
    """Decorator for pstats
    """
    collectorName = "Debug:%s" % func.__name__
    if hasattr(b_collector, 'custom_collectors'):
        if collectorName in b_collector.custom_collectors.keys():
            pstat = b_collector.custom_collectors[collectorName]
        else:
            b_collector.custom_collectors[collectorName] = PStatCollector(collectorName)
            pstat = b_collector.custom_collectors[collectorName]
    else:
        b_collector.custom_collectors = {}
        b_collector.custom_collectors[collectorName] = PStatCollector(collectorName)
        pstat = b_collector.custom_collectors[collectorName]
    b_collector.custom_collectors = {}
    b_collector.custom_collectors[collectorName] = PStatCollector(collectorName)
    pstat = b_collector.custom_collectors[collectorName]

    def doPstat(*args, **kargs):
        pstat.start()
        returned = func(*args, **kargs)
        pstat.stop()
        return returned
    doPstat.__name__ = func.__name__
    doPstat.__dict__ = func.__dict__
    doPstat.__doc__ = func.__doc__
    return doPstat

def makeCircle(vdata, numVertices=40,offset=Vec3(0,0,0), direction=1):
    circleGeom=Geom(vdata)

    vertWriter=GeomVertexWriter(vdata, "vertex")
    normalWriter=GeomVertexWriter(vdata, "normal")
    colorWriter=GeomVertexWriter(vdata, "color")
    uvWriter=GeomVertexWriter(vdata, "texcoord")
    drawWriter=GeomVertexWriter(vdata, "drawFlag")

    #make sure we start at the end of the GeomVertexData so we dont overwrite anything
    #that might be there already
    startRow=vdata.getNumRows()

    vertWriter.setRow(startRow)
    colorWriter.setRow(startRow)
    uvWriter.setRow(startRow)
    normalWriter.setRow(startRow)
    drawWriter.setRow(startRow)

    angle=2*math.pi/numVertices
    currAngle=angle

    for i in range(numVertices):
        position=Vec3(math.cos(currAngle)+offset.getX(), math.sin(currAngle)+offset.getY(),offset.getZ())
        vertWriter.addData3f(position)
        uvWriter.addData2f(position.getX()/2.0+0.5,position.getY()/2.0+0.5)
        colorWriter.addData4f(1.0, 1.0, 1.0, 1.0)
        position.setZ(position.getZ()*direction)
        position.normalize()
        normalWriter.addData3f(position)

        #at default Opengl only draws "front faces" (all shapes whose vertices are arranged CCW). We
        #need direction so we can specify which side we want to be the front face
        currAngle+=angle*direction

    circle=GeomTrifans(Geom.UHStatic)
    circle.addConsecutiveVertices(startRow, numVertices)
    circle.closePrimitive()

    circleGeom.addPrimitive(circle)

    return circleGeom

#Another helper function that I thought was to useful too throw away. Enjoy.
def makeCylinder(vdata,numVertices=40):
    topCircleGeom=makeCircle(vdata, numVertices,Vec3(0,0, 1))
    bottomCircleGeom=makeCircle(vdata, numVertices,Vec3(0,0,0),-1)


    body=GeomTristrips(Geom.UHStatic)

    j=40
    i=0
    while i < numVertices+1:
        body.addVertex(i)
        body.addVertex(j)
        i+=1
        if j==40:
            j=2*numVertices-1
        else:
            j-=1
        body.addVertex(i)
        body.addVertex(j)
        j-=1
        i+=1

    body.addVertex(numVertices-1)
    body.addVertex(0)
    body.addVertex(numVertices)
    body.closePrimitive()
    #print body



    cylinderGeom=Geom(vdata)

    cylinderGeom.addPrimitive(body)
    cylinderGeom.copyPrimitivesFrom(topCircleGeom)
    cylinderGeom.copyPrimitivesFrom(bottomCircleGeom)


    cylinderGeom.decomposeInPlace()
    cylinderGeom.unifyInPlace()
    return cylinderGeom


#this computes the new Axis which we'll make a branch grow alowng when we split
def randomAxis(vecList):
    fwd=vecList[0]
    perp1=vecList[1]
    perp2=vecList[2]

    nfwd=fwd+perp1*(2*random.random()-1) + perp2*(2*random.random()-1)
    nfwd.normalize()

    nperp2=nfwd.cross(perp1)
    nperp2.normalize()

    nperp1=nfwd.cross(nperp2)
    nperp1.normalize()

    return [nfwd, nperp1, nperp2]


#this makes smalle variations in direction when we are growing a branch but not splitting
def smallRandomAxis(vecList):
    fwd=vecList[0]
    perp1=vecList[1]
    perp2=vecList[2]

    nfwd=fwd+perp1*(1*random.random()-0.5) + perp2*(1*random.random()-0.5)
    nfwd.normalize()

    nperp2=nfwd.cross(perp1)
    nperp2.normalize()

    nperp1=nfwd.cross(nperp2)
    nperp1.normalize()

    return [nfwd, nperp1, nperp2]




#you cant normalize in-place so this is a helper function
def my_normalize(myVec):
    myVec.normalize()
    return myVec

#helper function to make a square given the Lower-Left-Hand and Upper-Right-Hand corners
def make_square(x1,y1,z1, x2,y2,z2, tex_coord):
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

    else:
        vertex.addData3f(x1, y1, z1)
        vertex.addData3f(x2, y2, z1)
        vertex.addData3f(x2, y2, z2)
        vertex.addData3f(x1, y1, z2)

    normal.addData3f(my_normalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
    normal.addData3f(my_normalize(Vec3(2*x2-1, 2*y2-1, 2*z1-1)))
    normal.addData3f(my_normalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
    normal.addData3f(my_normalize(Vec3(2*x1-1, 2*y1-1, 2*z2-1)))

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


# make square with 4 verticles
def make_square4v(coord1, coord2, coord3, coord4, tex_coord):
    format=GeomVertexFormat.getV3n3t2()
    vdata=GeomVertexData('square', format, Geom.UHStatic)

    x1, y1, z1 = coord1
    x2, y2, z2 = coord2
    x3, y3, z3 = coord3
    x4, y4, z4 = coord4

    vertex=GeomVertexWriter(vdata, 'vertex')
    normal=GeomVertexWriter(vdata, 'normal')
    texcoord=GeomVertexWriter(vdata, 'texcoord')

    #make sure we draw the sqaure in the right plane
    vertex.addData3f(x1, y1, z1)
    vertex.addData3f(x2, y2, z2)
    vertex.addData3f(x3, y3, z3)
    vertex.addData3f(x4, y4, z4)

    #normal.addData3f(Vec3(x1, y1, z1+10))
    #normal.addData3f(Vec3(x2, y2, z2+10))
    #normal.addData3f(Vec3(x3, y3, z3+10))
    #normal.addData3f(Vec3(x4, y4, z4+10))

    #normal.addData3f(Vec3(Vec3(coord2)-Vec3(coord1)).cross(Vec3(Vec3(coord3)-Vec3(coord1))))
    #normal.addData3f(Vec3(Vec3(coord2)-Vec3(coord1)).cross(Vec3(Vec3(coord3)-Vec3(coord1))))
    #normal.addData3f(Vec3(Vec3(coord2)-Vec3(coord1)).cross(Vec3(Vec3(coord3)-Vec3(coord1))))
    #normal.addData3f(Vec3(Vec3(coord4)-Vec3(coord1)).cross(Vec3(Vec3(coord3)-Vec3(coord1))))

    coord1 = Vec3(coord1)
    coord2 = Vec3(coord2)
    coord3 = Vec3(coord3)
    coord4 = Vec3(coord4)


    side1 = coord1 - coord2
    side2 = coord1 - coord4
    norm1 = side1.cross(side2)
    side1 = coord2 - coord3
    side2 = coord2 - coord4
    norm2 = side1.cross(side2)

    normal.addData3f(norm1)
    normal.addData3f(norm1)
    normal.addData3f(norm1)
    normal.addData3f(norm2)

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

    tri1.addVertex(0)
    tri1.addVertex(1)
    tri1.addVertex(3)

    tri1.addVertex(1)
    tri1.addVertex(2)
    tri1.addVertex(3)


    tri1.closePrimitive()

    square=Geom(vdata)
    square.addPrimitive(tri1)

    return square

# vi: ft=python:tw=0:ts=4

