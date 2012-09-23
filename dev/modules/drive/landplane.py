#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
land plane
"""
from pandac.PandaModules import Filename, CardMaker
from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
from pandac.PandaModules import PStatClient
from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib, TransparencyAttrib
from panda3d.core import RigidBodyCombiner, NodePath, Vec3
import time

class Chank(RigidBodyCombiner):
    """
        self.cubes[(x,y,z)] = name of type, or 'NULL'

        types:
            {'name': model}
    """
    def __init__(self, name, types, lod_node = None, lod = None):
        RigidBodyCombiner.__init__(self, name)
        self.types = types
        self.node = NodePath(self)

        self.node.reparentTo(render)
        # Why dont work? =(
        #if not lod_node:
            #self.node.reparentTo(render)
        #else:
            #lod.addSwitch(10.0, 5.0)
            #self.node.reparentTo(lod_node)
        #self.node.flattenLight()
        self.active = False

    def new(self, cubes):
        #tim = time.time()
        for cube in cubes:
            f = self.types[cubes[cube]].copyTo(self.node)
            f.setPos(cube)
        #print 'copy: ', time.time() - tim
        #tim = time.time()
        self.collect()
        #print 'collect: ', time.time() - tim
        self.active = True

    def show(self):
        if not self.active:
            self.node.show()
            self.active = True

    def hide(self):
        if self.active:
            self.node.hide()
            self.active = False

    def setPos(self, *args, **params):
        self.node.setPos(*args, **params)

    def setX(self, *args, **params):
        self.node.setX(*args, **params)

    def setY(self, *args, **params):
        self.node.setY(*args, **params)

    def destroy(self):
        self.node.removeNode()
        self.active = False

class LandNode():
    def __init__(self, x1, y1, x2, y2, z):
        maker = CardMaker( 'land' )
        maker.setFrame( x1, x2, y1, y2 )

        self.landNP = render.attachNewNode(maker.generate())
        self.landNP.setHpr(0,-90,0)
        self.landNP.setPos(0,0,z)
        self.landNP.setTransparency(TransparencyAttrib.MAlpha )

    def Destroy(self):
        base.graphicsEngine.removeWindow(self.buffer)
        self.cam.setInitialState(RenderState.makeEmpty())
        self.watercamNP.removeNode()
        self.landNP.clearShader()
        #self.bottomNP.removeNode()
        self.landNP.removeNode()


    def hide(self):
        self.landNP.hide()

    def show(self):
        self.landNP.show()


# vi: ft=python:tw=0:ts=4

