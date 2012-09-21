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


class CubesView(dict):
    """
        self[(x,y,z)] = name of type, or 'NULL'

        types:
            {'name': model}
    """
    def __init__(self, name, types, *args, **params):
        dict.__init__(self, *args, **params)
        self.rbc = RigidBodyCombiner(name)
        self.node = NodePath(self.rbc)
        self.node.reparentTo(render)
        self.types = types

    def show(self):
        for cube in self:
            if self[cube] == 'NULL':
                continue
            f = self.types[self[cube]].copyTo(self.node)
            f.setPos(cube)
        #f.detachNode()
        self.rbc.collect()

#class LandNode():
    #def __init__(self, x1, y1, x2, y2, z):
        #maker = CardMaker( 'land' )
        #maker.setFrame( x1, x2, y1, y2 )

        #self.landNP = render.attachNewNode(maker.generate())
        #self.landNP.setHpr(0,-90,0)
        #self.landNP.setPos(0,0,z)
        #self.landNP.setTransparency(TransparencyAttrib.MAlpha )


        #self.landPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )

        #planeNode = PlaneNode( 'landPlane' )
        #planeNode.setPlane( self.landPlane )

        ## Buffer and reflection camera
        #self.buffer = base.win.makeTextureBuffer( 'landBuffer', 256, 256 )
        #self.buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

        #cfa = CullFaceAttrib.makeReverse( )
        #rs = RenderState.make(cfa)

        ##self.landNP.setTexture(tex1)

    #def Destroy(self):
        #base.graphicsEngine.removeWindow(self.buffer)
        #self.cam.setInitialState(RenderState.makeEmpty())
        #self.watercamNP.removeNode()
        #self.landNP.clearShader()
        ##self.bottomNP.removeNode()
        #self.landNP.removeNode()


    #def hide(self):
        #self.landNP.hide()

    #def show(self):
        #self.landNP.show()


# vi: ft=python:tw=0:ts=4

