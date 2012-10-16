#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tree generator

Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
"""

import math, random, sys

from panda3d.core import Geom, GeomNode, GeomTristrips
from panda3d.core import GeomVertexArrayFormat, GeomVertexFormat
from panda3d.core import GeomVertexReader
from panda3d.core import GeomVertexRewriter
from panda3d.core import GeomVertexWriter
from panda3d.core import InternalName, NodePath
from panda3d.core import TransformState,CullFaceAttrib
from panda3d.core import Vec3,Vec4,Mat4
from pandac.PandaModules import PerlinNoise2
from voxplanet.support import randomAxis
from voxplanet.support import smallRandomAxis
from pandac.PandaModules import Texture, PNMImage

class TreeLand(dict):
    """Tree land - get number of TreeModel on the X, Y, Z coord

    config - voxplanet.config
    """
    def __init__(self, config, world):
        self.config = config
        self.world = world
        random.seed(self.world.seed)
        seed = random.randint(0, sys.maxint)
        self.perlin_trees = PerlinNoise2(sx = self.config.size_world, sy = self.config.size_world,
                                  table_size = 256, seed = seed)
        self.perlin_trees.setScale(2 ** (self.config.size_mod/32))
        seed = random.randint(0, sys.maxint)
        self.perlin_types = PerlinNoise2(sx = self.config.size_world, sy = self.config.size_world,
                                  table_size = 256, seed = seed)
        self.perlin_types.setScale(2 ** (self.config.size_mod/32))

    def gen_test_texture(self):
        image = PNMImage(256, 256)
        image.fill(100,100,100)
        for x in xrange(0, 256):
            for y in xrange(0, 256):
                r = 100
                g = 100
                b = 100
                if self[x, y, 3] != None:
                    r = 0
                    g = 100
                    b = 0
                image.setPixel(x, y, (r, g, b))

        texture = Texture()
        texture.load(image)
        return texture

    def __getitem__(self, item):
        """item - X, Y, Z - return Tree Info

        """
        x, y, z = item
        if 1 <= z <= self.config.low_mount_level[1]:
            t = round(self.perlin_trees(x, y),3)
            if t >= 0.9 or (0.5 <= t <= 0.51):
                tp = abs(self.perlin_types(x, y))
                tp = tp * (len(self.world.trees)-1)
                return int(round(tp))
            else:
                return None
        else:
            return None

# Shit for fucking trees

formatArray = GeomVertexArrayFormat()
formatArray.addColumn(InternalName.make("drawFlag"), 1, Geom.NTUint8, Geom.COther)

treeform = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
treeform.addArray(formatArray)
treeform = GeomVertexFormat.registerFormat(treeform)


#this draws the body of the tree. This draws a ring of vertices and connects the rings with
#triangles to form the body.
#this keepDrawing paramter tells the function wheter or not we're at an end
#if the vertices before you were an end, dont draw branches to it
def draw_body(nodePath, vdata, pos, vecList, radius=1, keepDrawing=True,numVertices=8):

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
def draw_leaf(nodePath,vdata, pos=Vec3(0,0,0),vecList=[Vec3(0,0,1), Vec3(1,0,0),Vec3(0,-1,0)], scale=0.125):

    #use the vectors that describe the direction the branch grows to make the right
        #rotation matrix
    newCs=Mat4(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    newCs.setRow(0, vecList[2]) #right
    newCs.setRow(1, vecList[1]) #up
    newCs.setRow(2, vecList[0]) #forward
    newCs.setRow(3, Vec3(0,0,0))
    newCs.setCol(3,Vec4(0,0,0,1))

    try:
        axisAdj=Mat4.scaleMat(scale)*newCs*Mat4.translateMat(pos)
    except TypeError, e:
        print e
        print scale, pos

    #orginlly made the leaf out of geometry but that didnt look good
    #I also think there should be a better way to handle the leaf texture other than
    #hardcoding the filename
    #leafModel=loader.loadModel('models/shrubbery')
    #leafTexture=loader.loadTexture('models/material-10-cl.png')

    leafModel = NodePath('leaf')
    nodePath.leafModel.copyTo(leafModel)
    leafModel.reparentTo(nodePath)
    leafModel.setTexture(nodePath.leafTex,1)
    leafModel.setTransform(TransformState.makeMat(axisAdj))

#recursive algorthim to make the tree
def make_fractal_tree(bodydata, nodePath,length, pos=Vec3(0,0,0), numIterations=11, numCopies=4,vecList=[Vec3(0,0,1),Vec3(1,0,0), Vec3(0,-1,0)]):
    if numIterations>0:

        draw_body(nodePath, bodydata, pos, vecList, length.getX())


        #move foward along the right axis
        newPos=pos+vecList[0]*length.length()


        #only branch every third level (sorta)
        if numIterations%3==0:
            #decrease dimensions when we branch
            length=Vec3(length.getX()/2, length.getY()/2, length.getZ()/1.1)
            for i in range(numCopies):
                make_fractal_tree(bodydata, nodePath,length,newPos, numIterations-1, numCopies,randomAxis(vecList))
        else:
            #just make another branch connected to this one with a small variation in direction
            make_fractal_tree(bodydata, nodePath,length,newPos, numIterations-1,numCopies,smallRandomAxis(vecList))

    else:
        draw_body(nodePath,bodydata, pos, vecList, length.getX(),False)
        draw_leaf(nodePath,bodydata, pos, vecList)


# vi: ft=python:tw=0:ts=4

