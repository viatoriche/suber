#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""
from pandac.PandaModules import GeoMipTerrain,Filename, BitMask32
from pandac.PandaModules import Texture,TextureStage
from pandac.PandaModules import AmbientLight, PointLight

from pandac.PandaModules import Vec4
from pandac.PandaModules import Texture, PNMImage
from modules.drive.waterplane1 import WaterNode

class gameLocation():
    def __init__(self):
        self.terrain=GeoMipTerrain("Terrain")
        taskMgr.add(self.update,'location_update')
        self._water_level = Vec4(0.0, 0.0, 0.45, 1.0)

    def loadTerrain(self, heights_file):
        #self.terrain.setHeightfield(heights_file)
        self.terrain.setHeightfield(heights_file)
        self.terrain.setBlockSize(16)
        self.terrain.setFactor(32)
        #self.terrain.setMinLevel(2)
        self.terrain.getRoot().reparentTo(render)
        self.terrain.getRoot().setSz (30)
        self.terrain.generate()
        self.terrain.setFocalPoint(base.camera)
        gnodes=self.terrain.getRoot().findAllMatches("+GeomNode")
        for gnode in gnodes:
            gnode.node().setIntoCollideMask(BitMask32.bit(1))

        self.att_water = WaterNode(0,0,256,256, self._water_level.getZ())

        #self.att_water.changeParams(None)
        #wl=self._water_level
        #wl.setZ(wl.getZ()-0.05)    # add some leeway (gets rid of some mirroring artifacts)
        #root = self.terrain.getRoot()
        #root.setShaderInput('waterlevel', self._water_level)

        #render.setShaderInput('time', 0)

    def setTexture(self,texFile,sx,sy):
        self.terrain.getRoot().setTexture(loader.loadTexture(texFile))
        self.terrain.getRoot().setTexScale(TextureStage.getDefault(), sx, sy)
        self.terrain.getRoot().getTexture().setMinfilter(Texture.FTLinearMipmapLinear)

    def setLights(self,ambient_l,camera_l):
        self.ambientLight = render.attachNewNode( AmbientLight( "ambientLight" ))
        self.pointLight = camera.attachNewNode( PointLight( "PointLight" ) )
        self.ambientLight.node().setColor(ambient_l)
        self.pointLight.node().setColor(camera_l)
        render.setLight( self.ambientLight )
        render.setLight( self.pointLight )

    def update(self,task):
        self.terrain.update()
        #self.terrain.getRoot().setRenderModeWireframe()
        return task.cont

class World():
    """
    docstring for World
    """
    map_2d = None
    map_3d = None

def show_terrain(heightmap):
    loc=gameLocation()
    loc.loadTerrain(heightmap)
    loc.setTexture('res/textures/dirt.png',20,20)
    loc.setLights(Vec4(0.6,0.6,0.6,1), Vec4(1,1,1,1))

def generate_heights_image(map_world):
    size = map_world.size
    image = PNMImage(size, size)
    image.fill(0,0,0)
    for x, y in map_world:
        val = map_world[(x, y)]
        image.setPixel(x, y, (val, val, val))
    return image

def generate_map_texture(map_world):
    size = map_world.size
    image = PNMImage(size, size)
    image.fill(0,0,0)
    for x, y in map_world:
        if map_world[(x, y)] <= map_world.water_z:
            image.setPixel(x, y, (0, 0, 255-map_world[(x, y)]))
        else:
            image.setPixel(x, y, (0, 255-map_world[(x, y)], 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

