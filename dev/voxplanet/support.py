#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Support functions for generate models and other
"""

import math, random

from panda3d.core import InternalName
from panda3d.core import Geom, GeomNode, GeomTrifans, GeomTristrips
from panda3d.core import GeomTriangles, GeomVertexWriter
from panda3d.core import GeomVertexArrayFormat, GeomVertexFormat
from panda3d.core import GeomVertexReader
from panda3d.core import GeomVertexRewriter, GeomVertexData
from panda3d.core import TransformState,CullFaceAttrib
from panda3d.core import Vec3,Vec4,Mat4

#this is a helper function you can use to make a circle in the x-y plane
#i didnt end up needing it but this comes up fairly often so I thought
#I should keep this in the code. Feel free to use.

from panda3d.core import PStatCollector
import cProfile

class BCol():
    custom_collectors = {}

b_collector = BCol()

def profile_decorator(func):
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
        #cprofile.create_stats()
        returned = func(*args, **kargs)
        #cprofile.print_stats()
        #returned = func(*args, **kargs)
        pstat.stop()
        return returned
    doPstat.__name__ = func.__name__
    doPstat.__dict__ = func.__dict__
    doPstat.__doc__ = func.__doc__
    return doPstat

formatArray = GeomVertexArrayFormat()
formatArray.addColumn(InternalName.make("drawFlag"), 1, Geom.NTUint8, Geom.COther)

treeform = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
treeform.addArray(formatArray)
treeform = GeomVertexFormat.registerFormat(treeform)

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



#this draws the body of the tree. This draws a ring of vertices and connects the rings with
#triangles to form the body.
#this keepDrawing paramter tells the function wheter or not we're at an end
#if the vertices before you were an end, dont draw branches to it
def drawBody(nodePath, vdata, pos, vecList, radius=1, keepDrawing=True,numVertices=8):

    circleGeom=Geom(vdata)

    vertWriter=GeomVertexWriter(vdata, "vertex")
    colorWriter=GeomVertexWriter(vdata, "color")
    normalWriter=GeomVertexWriter(vdata, "normal")
    drawReWriter=GeomVertexRewriter(vdata, "drawFlag")
    texReWriter=GeomVertexRewriter(vdata, "texcoord")


    startRow=vdata.getNumRows()
    vertWriter.setRow(startRow)
    colorWriter.setRow(startRow)
    normalWriter.setRow(startRow)

    sCoord=0

    if (startRow!=0):
        texReWriter.setRow(startRow-numVertices)
        sCoord=texReWriter.getData2f().getX()+1

        drawReWriter.setRow(startRow-numVertices)
        if(drawReWriter.getData1f()==False):
            sCoord-=1

    drawReWriter.setRow(startRow)
    texReWriter.setRow(startRow)

    angleSlice=2*math.pi/numVertices
    currAngle=0

    #axisAdj=Mat4.rotateMat(45, axis)*Mat4.scaleMat(radius)*Mat4.translateMat(pos)

    perp1=vecList[1]
    perp2=vecList[2]

    #vertex information is written here
    for i in range(numVertices):
        adjCircle=pos+(perp1*math.cos(currAngle)+perp2*math.sin(currAngle))*radius
        normal=perp1*math.cos(currAngle)+perp2*math.sin(currAngle)
        normalWriter.addData3f(normal)
        vertWriter.addData3f(adjCircle)
        texReWriter.addData2f(sCoord,(i+0.001)/(numVertices-1))
        colorWriter.addData4f(0.5,0.5,0.5,1)
        drawReWriter.addData1f(keepDrawing)
        currAngle+=angleSlice


    drawReader=GeomVertexReader(vdata, "drawFlag")
    drawReader.setRow(startRow-numVertices)

    #we cant draw quads directly so we use Tristrips
    if (startRow!=0) & (drawReader.getData1f()!=False):
        lines=GeomTristrips(Geom.UHStatic)
        half=int(numVertices*0.5)
        for i in range(numVertices):
            lines.addVertex(i+startRow)
            if i< half:
                lines.addVertex(i+startRow-half)
            else:
                lines.addVertex(i+startRow-half-numVertices)

        lines.addVertex(startRow)
        lines.addVertex(startRow-half)
        lines.closePrimitive()
        lines.decompose()
        circleGeom.addPrimitive(lines)


        circleGeomNode=GeomNode("Debug")
        circleGeomNode.addGeom(circleGeom)

        #I accidentally made the front-face face inwards. Make reverse makes the tree render properly and
            #should cause any surprises to any poor programmer that tries to use this code
        circleGeomNode.setAttrib(CullFaceAttrib.makeReverse(),1)
        #nodePath.numPrimitives+=numVertices*2

        nodePath.attachNewNode(circleGeomNode)

#this draws leafs when we reach an end
def drawLeaf(nodePath,vdata, leafModel, pos=Vec3(0,0,0),vecList=[Vec3(0,0,1), Vec3(1,0,0),Vec3(0,-1,0)], scale=0.125):

    #use the vectors that describe the direction the branch grows to make the right
        #rotation matrix
    newCs=Mat4(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    newCs.setRow(0, vecList[2]) #right
    newCs.setRow(1, vecList[1]) #up
    newCs.setRow(2, vecList[0]) #forward
    newCs.setRow(3, Vec3(0,0,0))
    newCs.setCol(3,Vec4(0,0,0,1))

    axisAdj=Mat4.scaleMat(scale)*newCs*Mat4.translateMat(pos)

    #orginlly made the leaf out of geometry but that didnt look good
    #I also think there should be a better way to handle the leaf texture other than
    #hardcoding the filename
    #leafModel=loader.loadModel('models/shrubbery')
    #leafTexture=loader.loadTexture('models/material-10-cl.png')


    leafModel.reparentTo(nodePath)
    #leafModel.setTexture(leafTexture,1)
    leafModel.setTransform(TransformState.makeMat(axisAdj))

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

def makeSquare_net(coord1, coord2, coord3, coord4, tex_coord):
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

    tri1.addVertex(1)
    tri1.addVertex(2)
    tri1.addVertex(3)


    tri1.closePrimitive()
    tri2.closePrimitive()

    square=Geom(vdata)
    square.addPrimitive(tri1)
    square.addPrimitive(tri2)

    return square

# vi: ft=python:tw=0:ts=4

