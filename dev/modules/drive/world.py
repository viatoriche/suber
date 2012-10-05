#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
World
"""

import random
import sys
import math
import time

from modules.drive.landplane import LandNode, ChunkModel
from modules.drive.shapeGenerator import Cube as CubeModel
from panda3d.core import Vec3
from modules.drive.textures import textures
from panda3d.core import NodePath
from pandac.PandaModules import Texture, TextureStage
from panda3d.core import VBase3
from config import Config
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from modules.drive.support import ThreadPandaDo
import sys

#sys.setrecursionlimit(65535)

class WaterNode():
    """Water plane for nya

    """
    config = Config()
    def __init__(self, water_z):
        self.water_z = water_z
        self.create(0, 0, (self.config.size_world/8, self.config.size_world/8))

    def create(self, x, y, scale):
        self.water = LandNode(self.water_z)
        #textures['water'].setWrapU(Texture.WMRepeat)
        #textures['water'].setWrapV(Texture.WMRepeat)
        ts = TextureStage('ts')
        #ts.setMode(TextureStage.MDecal)
        self.water.landNP.setTransparency(TransparencyAttrib.MAlpha)
        self.water.landNP.setTexture(ts, textures['water'])
        scale_x, scale_y = scale
        self.water.landNP.setTexScale(ts, scale_x, scale_y)

    def show(self):
        self.water.landNP.show()

    def hide(self):
        self.water.landNP.hide()

    def reset(self, x, y):
        #self.Destroy()
        #self.create(x, y)
        self.water.landNP.show()
        try:
            self.water.landNP.setPos(x, y, self.water_z)
        except:
            pass

class QuadroTreeNode:
    """Node - one cube, which may divide on 4 cubes, when camera is near

    Node = X, Y, where Z - height from perlin noize generator -> perlin(x, y, level)

    X,Y this is one of 64 x 64 global map height

    level - depend of height camera
    """
    # exist = True #make voxel deletable by player
    childs = {}
    def __init__(self, chunks_clt, len_chunk, parent=None,\
                       level = 1, center = (0,0,0)):

        #print 'Create node: ', len_chunk, level, center
        self.parent = parent
        self.level = level
        self.chunks_clt = chunks_clt
        self.world = chunks_clt.world
        self.chunks_map = chunks_clt.chunks_map
        self.len_chunk = len_chunk
        x = center[0]
        y = center[1]
        z = 0
        self.center = x, y, z
        #if self.parent:
            #print '>>>>>>>>> init: --- show : ', self.center, ' parent: ', self.parent.center
        #else:
            #print '>>>>>>>>> init: --- show : ', self.center, ' parent: NONE. I am ROOT'
        self.show()
        #print 'init: ', center, len_chunk

    def repaint(self):
        if self.len_chunk > self.chunks_map.chunk_len:
            factor = 1
            trigger_dist = self.len_chunk * factor
            # self.chunks_map.camPos
            length_cam = VBase3.length(Vec3(self.center) - self.chunks_map.camPos)
            if length_cam < trigger_dist:
                #print '\t~~~~~~~~ Cam dist ok: ---- ', self.center, ' cam: ', trigger_dist, length_cam
                self.hide()
                self.divide()
            else:
                #print '\t~~~~~~~~ Cam dist not ok ----- show myself: ', self.center, ' cam: ', trigger_dist, length_cam
                #self.hide_childs()
                self.show()
        else:
            #print '\t:::::::: repaint: len <= min_len  -- show'
            self.show()

    def show_childs(self):
        for child in self.childs:
            self.childs[child].show()

    def hide_childs(self):
        for child in self.childs:
            self.childs[child].hide()


    def divide(self):
        #print '\t\t\t xxx START DIVIDE: ', self.center
        self.childs = {}
        new_len = self.len_chunk/2
        new_center = self.len_chunk/4
        #name = self.center + dC * self.len_chunk
        # <- up
        name = self.center[0] - new_center, self.center[1] - new_center, 0
        self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                self.level+1, name)
        self.childs[name].repaint()
        # -> up
        name = self.center[0] + new_center, self.center[1] - new_center, 0
        self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                self.level+1, name)
        self.childs[name].repaint()
        # <- down
        name = self.center[0] - new_center, self.center[1] + new_center, 0
        self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                self.level+1, name)
        self.childs[name].repaint()
        # -> down
        name = self.center[0] + new_center, self.center[1] + new_center, 0
        self.childs[name] = QuadroTreeNode(self.chunks_clt, new_len, self, \
                self.level+1, name)
        self.childs[name].repaint()

        #print '\t+++++++ DIVIDE SHOW ++++++++', self.center
        #self.show()

        #for child in self.childs:
            ##print 'Child of ', self.center, ' ----> ', child
            #if not self.childs[child].isHidden:
                #print '\t\t========== Child: ', child, ' not hidden, hide myself: ', self.center
                #self.hide()
                #break

    def show(self):
        self.isHidden = False
        self.chunks_clt.chunks[self.center, self.len_chunk, self.level] = True

    def hide(self):
        self.isHidden = True
        self.chunks_clt.chunks[self.center, self.len_chunk, self.level] = False

class ChunksCollection():
    #v = [
         #Vec3(0., 0.5, 0.), Vec3(0.5, 0., 0.),
         #Vec3(0., 0., 0.), Vec3(0.5, 0.5, 0.),
         #]

    config = Config()
    chunks = {}
    thread_done = True

    def __init__(self, chunks_map, world, center, max_len):

        self.center = center

        self.max_len = max_len
        self.chunks_map = chunks_map

        self.world = world

        self.root = QuadroTreeNode(self, self.max_len, center = self.center)
        self.chunks_models = {}

        self.generate()
        self.show()

    def generate(self):
        for chunk in self.chunks:
            self.chunks[chunk] = False
        self.root.repaint()

    def show(self):
        # TODO: add delete cube event

        for chunk_model in self.chunks_models:
            if not self.chunks[chunk_model]:
                if not self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].hide()
            else:
                if self.chunks_models[chunk_model].isHidden():
                    self.chunks_models[chunk_model].show()

        for chunk in self.chunks:
            if not self.chunks_models.has_key(chunk):
                # TODO: CubeModel --> ChunkModel
                #self.chunks_models[chunk] = CubeModel(chunk[1], chunk[1], chunk[1])
                #self.chunks_models[chunk] = ChunkModel(self.world, chunk[0][0], chunk[0][1], chunk[1])
                self.chunks_models[chunk] = ChunkModel(self.world, chunk[0][0], chunk[0][1], chunk[1])
                #self.world.root_node.attachNewNode(self.chunks_models[chunk])
                self.chunks_models[chunk].reparentTo(self.world.root_node)
                #self.chunks_models[chunk].setZ(chunk[2])
                #height = self.world.map_3d[chunk[0][0], chunk[0][1]]
                #texturization
                #if height <= 0:
                    #self.chunks_models[chunk].setTexture(textures['sand'])
                #elif height >= self.config.land_mount_level[0] and height <= self.config.land_mount_level[1]:
                    #self.chunks_models[chunk].setTexture(textures[self.config.land_mount_level])
                #elif height >= self.config.low_mount_level[0] and height <= self.config.low_mount_level[1]:
                    #self.chunks_models[chunk].setTexture(textures[self.config.low_mount_level])
                #elif height >= self.config.mid_mount_level[0] and height <= self.config.mid_mount_level[1]:
                    #self.chunks_models[chunk].setTexture(textures[self.config.mid_mount_level])
                #elif height >= self.config.high_mount_level[0]:
                    #self.chunks_models[chunk].setTexture(textures[self.config.high_mount_level])

                #self.chunks_models[chunk].setPos(chunk[0][0]+random.randint(0, 10000), chunk[0][1]+random.randint(0, 10000), 0)
                #print 'Create: ', chunk

            #if self.chunks[chunk]:
                #if self.chunks_models[chunk].isHidden():
                    #self.chunks_models[chunk].show()
            #else:
                #if not self.chunks_models[chunk].isHidden():
                    #self.chunks_models[chunk].hide()

class ChunksMap():
    config = Config()
    chunk_len = 16
    def __init__(self, world, size, level):
        self.world = world
        self.level = level
        self.size = size
        self.max_len = self.config.size_world
        self.chunks_clts = {}
        #base.camera.setPos(self.max_len/2, self.max_len/2, 53000000)
        base.camera.setPos(0, 0, 10)
        #base.camera.setPos(0, 0, 25000000)
        self.camPos = base.camera.getPos(self.world.root_node)
        self.get_coords()
        self.create()

    def get_coords(self):
        self.camX = int(base.camera.getX(self.world.root_node))
        self.camY = int(base.camera.getY(self.world.root_node))
        self.camZ = int(base.camera.getZ(self.world.root_node))
        self.land_z = int(self.world.map_3d[self.camX, self.camY])
        self.far = self.max_len
        if self.far < 2000:
            self.far = 2000
        base.camLens.setFar(self.far)
        self.camPos = base.camera.getPos(self.world.root_node)

    def show(self):
        if self.camPos != base.camera.getPos(self.world.root_node):
            self.get_coords()
            self.world.game.write('CamPos: X: {0}, Y: {1}, Z: {2}, '\
                              'land height: {3}'.format(self.camX, self.camY, self.camZ,
                               self.land_z))

            for chunks_clt in self.chunks_clts.values():
                chunks_clt.generate()
                chunks_clt.show()

    def create(self):
        for x in xrange(-self.size, self.size+1):
            for y in xrange(-self.size, self.size+1):
                name = (x*self.max_len)+(self.max_len / 2), (y*self.max_len) + (self.max_len / 2), 0
                self.chunks_clts[name] = ChunksCollection(self, self.world, name, self.max_len)


class World():
    config = Config()
    def __init__(self, gui, game):
        self.level = self.config.root_level
        self.seed = random.randint(0, sys.maxint)
        self.game = game
        self.gui = gui
        self.loader = self.gui.app.loader
        loader = self.loader
        self.root_node = NodePath('ROOT')
        self.root_node.reparentTo(render)
        self.root_node.setX(-100000)

        land_mount_level = self.config.land_mount_level
        low_mount_level = self.config.low_mount_level
        mid_mount_level = self.config.mid_mount_level
        high_mount_level = self.config.high_mount_level

        textures[land_mount_level] = loader.loadTexture("res/textures/land.png")
        textures[land_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[land_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[low_mount_level] = loader.loadTexture("res/textures/low_mount.png")
        textures[low_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[low_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[mid_mount_level] = loader.loadTexture("res/textures/mid_mount.png")
        textures[mid_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[mid_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures[high_mount_level] = loader.loadTexture("res/textures/high_mount.png")
        textures[high_mount_level].setMagfilter(Texture.FTLinearMipmapLinear)
        textures[high_mount_level].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['water'] = loader.loadTexture("res/textures/water.png")
        textures['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['black'] = loader.loadTexture("res/textures/black.png")
        textures['black'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['black'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['sand'] = loader.loadTexture("res/textures/sand.png")
        textures['sand'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['sand'].setMinfilter(Texture.FTLinearMipmapLinear)

        #self.cube_size = self.config.cube_size
        #self.cube_z = 1
        #self.types = {}

        #self.types[land_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.types[land_mount_level].setTexture(textures[land_mount_level],1)

        #self.types[low_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.types[low_mount_level].setTexture(textures[low_mount_level],1)

        #self.types[mid_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.types[mid_mount_level].setTexture(textures[mid_mount_level],1)

        #self.types[high_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.types[high_mount_level].setTexture(textures[high_mount_level],1)

        #self.types['sand'] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.types['sand'].setTexture(textures['sand'],1)

        #self.cubik = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        #self.cubik.reparentTo(self.gui.app.render)
        #self.cubik.setTexture(textures[high_mount_level],1)

        #self.water = WaterNode(1)
        #self.water.show()


    def new(self):
        """New world
        """
        textures['world_map'] = textures.get_map_3d_tex(self, 512)
        textures['world_map'].setWrapU(Texture.WMMirrorOnce)
        textures['world_map'].setWrapV(Texture.WMMirrorOnce)
        ts = TextureStage('world_map_ts')
        #self.cubik.setTexture(ts, textures['world_map'])
        #self.cubik.setTexScale(ts, 0.5, 0.5)
        self.chunks_map = ChunksMap(self, 0, 1)

    def show(self):
        self.chunks_map.show()

# vi: ft=python:tw=0:ts=4

