#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""

import sys, random
import time

from modules.drive.landplane import Chank, LandNode
from modules.drive.shapeGenerator import Cube as CubeModel
from modules.drive.textures import textures
from modules.world.map3d import generate_heights
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage, PNMImage

class WaterNode():
    """Water plane for nya

    """
    def __init__(self, water_z):
        self.water_z = water_z

    def create(self, x, y):
        self.water = LandNode(self.water_z)
        #textures['water'].setWrapU(Texture.WMRepeat)
        #textures['water'].setWrapV(Texture.WMRepeat)
        ts = TextureStage('ts')
        #ts.setMode(TextureStage.MDecal)
        self.water.landNP.setTransparency(TransparencyAttrib.MAlpha)
        self.water.landNP.setTexture(ts, textures['water'])
        self.water.landNP.setTexScale(ts, 256, 256)

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

class MapTree():
    """Tree of Maps level
    """
    # map_tree ---
    map3d = None
    coords = (0, 0, 64)
    maps = {}
    child = None
    def __init__(self, parent = None, name = None):
        self.parent = parent
        self.name = name
        if self.parent:
            start_x, start_y = name
            self.gen_down_coords()
            print 'Name: ', name, '/', self.parent.name, 'Parent: ', self.parent.coords, ' self: ', self.coords
            t = time.time()
            self.map3d = generate_heights(self.parent.map3d, start_x, start_y)
            print 'generate map:', time.time() - t

    def gen_down_coords(self):
        """Generate self.coords, when def down is run
        """
        x, y, z = self.parent.coords
        start_x, start_y = self.name
        cur_x = (x - (start_x * 16)) * 16
        cur_y = (y - (start_y * 16)) * 16
        self.coords = (cur_x, cur_y, 64)

    def down(self):
        """Create new MapTree and join
        """
        x, y, z = self.coords
        name = x / 16, y / 16
        return MapTree(self, name)

    def change_parent_coords(self):
        """Change parent coordinates when child is moving
        """
        if self.parent:
            cur_x, cur_y, cur_z = self.coords
            start_x, start_y = self.name
            x = (cur_x / 16) + (start_x * 16)
            y = (cur_y / 16) + (start_y * 16)
            self.parent.coords = (x, y, 64)
            #print 'Parent: ', self.parent.coords, ' self: ', self.coords

    def get_map(self, mapX, mapY, Join = False):
        """Get map for new name, and join to, if Join == True
        """
        if (mapX, mapY) == (0, 0):
            return self.map3d

        if self.parent:
            name_X, name_Y = self.name
            mapX, mapY = name_X + mapX, name_Y + mapY
            if self.name == (mapX, mapY):
                map3d = self.map3d
            else:
                #import pdb
                #pdb.set_trace()
                parent_X, parent_Y = 0, 0
                if mapX > 15:
                    mapX = mapX - 15
                    parent_X = 1
                if mapX < 0:
                    mapX = mapX + 15
                    parent_X = -1
                if mapY > 15:
                    mapY = mapY - 15
                    parent_Y = 1
                if mapY < 0:
                    mapY = mapY + 15
                    parent_Y = -1

                # Oh, I love recurses :3
                if self.maps.has_key( (mapX, mapY) ):
                    map3d = self.maps[ (mapX, mapY) ]
                else:
                    source_map = self.parent.get_map(parent_X, parent_Y, Join = Join)
                    print 'Start generate of map X.Y:', mapX, mapY,' / Name: ', self.name, '/', self.parent.name, 'Parent: ', self.parent.coords, ' self: ', self.coords
                    t = time.time()
                    map3d = generate_heights(source_map, mapX, mapY)
                    print 'generate map:', time.time() - t
                    self.maps[ (mapX, mapY) ] = map3d
                    if Join:
                        self.name = mapX, mapY
                        print 'We are joined to: ', self.name
                        self.map3d = map3d
        # If we are 16 lvl (high-end)
        else:
            map3d = self.map3d
        return map3d

    def get_coords_txt(self, level, cam):
        cur_x, cur_y, cur_z = self.coords
        x, y, z = cam
        cam = int(x), int(y), int(z)
        if self.parent:
            par_x, par_y, par_z = self.parent.coords
            return 'L:{8} * X: {0}, Y: {1} -> {2}:{3} * UX: {4}, UY: {5} -> {6}:{7} | cube = {9} | {10}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, par_x, par_y, par_x/16, par_y/16, level, self.map3d[(cur_x, cur_y)], cam)
        else:
            return 'L:{4} * X: {0}, Y: {1} -> {2}:{3} | cube z = {5} | {6}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, level, self.map3d[(cur_x, cur_y)], cam)


    #def up

class World():
    """
    docstring for World
    """
    map_2d = None
    # kawaii tech for LoD of World, logic Tree based
    map_tree = None
    # chanks {level: {(x, y): Chank}}, where x, y = X*16, Y*16 with cubes
    chanks_map = {}
    size_chank = 16
    # modelles with texture for cubes
    types = {}
    def __init__(self):
        self.seed = random.randint(0, sys.maxint)
        self.chank_changed = True
        self.level = 16
        self.new = True
        self.water_node = WaterNode(0.5)
        textures['dirt'] = loader.loadTexture("res/textures/dirt.png")
        textures['dirt'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['dirt'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['water'] = loader.loadTexture("res/textures/water.png")
        textures['water'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['water'].setMinfilter(Texture.FTLinearMipmapLinear)

        textures['sand'] = loader.loadTexture("res/textures/sand.png")
        textures['sand'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['sand'].setMinfilter(Texture.FTLinearMipmapLinear)

        self.water_node.create(0, 0)
        self.cube_size = 1
        self.cube_z = 16
        self.types['land'] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types['land'].setTexture(textures['dirt'],1)
        self.types['water'] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types['water'].setTexture(textures['sand'],1)

        self.paint_thread = False

        for i in xrange(1,17):
            self.chanks_map[i] = {}

def show_terrain(game, cam_coords, level):
    if game.world.paint_thread:
        return

    change_level = False

    size_chank = game.world.size_chank

    camX, camY, camZ = cam_coords

    OK = False

    OK = game.world.new
    game.world.new = False

    last_level = game.world.level
    game.world.level = level
    if level == last_level:

        lastX, lastY, lastZ = game.world.map_tree.coords

        X = int(camX) / 256
        X = X * 256
        X = int(camX) - X

        Y = int(camY) / 256
        Y = Y * 256
        Y = int(camY) - Y

        Z = int(camZ)

        if (lastX, lastY, lastZ) != (X, Y, Z):

            mapX, mapY = 0, 0
            if lastX == 0:
                mapX = 1
            if lastX == 255:
                mapX = -1
            if lastY == 0:
                mapY = 1
            if lastY == 255:
                mapY = -1
            game.world.map_tree.get_map(mapX, mapY, True)

            #game.world.water_node.reset(int(camX/16)*16, int(camY/16)*16)

            game.world.map_tree.coords = (X, Y, Z)
            game.world.map_tree.change_parent_coords()
            game.write(game.world.map_tree.get_coords_txt(level, cam_coords))

    # down / up
    else:
        for ch in game.world.chanks_map[last_level]:
            game.world.chanks_map[last_level][ch].destroy()

        game.world.chanks_map[last_level] = {}

        game.world.chank_changed = True

        if level < last_level:
            game.world.map_tree = game.world.map_tree.down()
        if level > last_level:
            game.world.map_tree = game.world.map_tree.parent

        X, Y, Z = game.world.map_tree.coords
        game.world.map_tree.change_parent_coords()
        game.write(game.world.map_tree.get_coords_txt(level, cam_coords))
        lastX, lastY, lastZ = game.world.map_tree.coords
        base.camera.setX(X)
        base.camera.setY(Y)
        camX, camY, camZ = X, Y, base.camera.getZ()
        OK = True
        change_level = True

    if (lastX, lastY) != (X, Y):
        OK = True

    if not OK:
        return

    cur_map = game.world.map_tree.map3d
    if (X / size_chank, Y / size_chank) != (lastX / size_chank, lastY / size_chank):
        for ch in game.world.chanks_map[level].values():
            ch.hide()
        game.world.chank_changed = True

    game.cmd_handle('showmap')

    if not game.world.chank_changed:
        return


    def Paint():
        """Create cubes on screen
        """

        t= time.time()

        cube_size = game.world.cube_size
        types = game.world.types

        chanks = 3

        dx = ((X / size_chank) - chanks) * size_chank
        for xcount in xrange(chanks * 2):
            dy = ((Y / size_chank) - chanks) * size_chank
            for ycount in xrange(chanks * 2):
                chank_X = dx + (256 * (int(camX)/256))
                chank_Y = dy + (256 * (int(camY)/256))
                water_X = chank_X - 80
                water_Y = chank_Y - 80
                game.world.water_node.reset(water_X, water_Y)
                
                cubes = {}
                time_gen = time.time()
                for x in xrange(dx, dx + size_chank):
                    mapX = 0
                    cX = x
                    if cX < 0:
                        cX = 255+cX
                        mapX = -1
                    if cX > 255:
                        cX = cX-255
                        mapX = 1
                    for y in xrange(dy, dy + size_chank):
                        mapY = 0
                        cY = y
                        if cY < 0:
                            cY = 255+cY
                            mapY = -1
                        if cY > 255:
                            cY = cY-255
                            mapY = 1

                        cur_map = game.world.map_tree.get_map(mapX, mapY, False)

                        cube_X = x + (256 * (int(camX)/256))
                        cube_Y = y + (256 * (int(camY)/256))
                        cube_X = cube_X * cube_size
                        cube_Y = cube_Y * cube_size
                        if cur_map[(cX, cY)]<=cur_map.water_z:
                            cubes[(cube_X, cube_Y, cur_map[cX,cY] - game.world.cube_z)] = 'water'
                        else:
                            cubes[(cube_X, cube_Y, cur_map[cX,cY] - game.world.cube_z)] = 'land'

                #print 'time gen cubes: ', time.time() - time_gen

                #time_create = time.time()
                if game.world.chanks_map[level].has_key((chank_X, chank_Y)):
                    if game.world.chanks_map[level][(chank_X, chank_Y)].cubes == cubes:
                        time_show = time.time()
                        game.world.chanks_map[level][(chank_X, chank_Y)].show()
                    else:
                        game.world.chanks_map[level][(chank_X, chank_Y)].new(cubes)
                else:
                    ch = Chank('ch_{0}_{1}_{2}'.format(level, chank_X, chank_Y),
                                                   types, game.process.lod_node,
                                                   game.process.lod)
                    ch.new(cubes)
                    game.world.chanks_map[level][(chank_X, chank_Y)] = ch

                #print 'time create chank: ', time.time() - time_create
                dy += size_chank
            dx += size_chank

        #print 'show', time.time()-t
        game.world.chank_changed = False
        game.world.paint_thread = False

    game.world.paint_thread = True
    Paint()
    if change_level:
        change_level = False
        base.camera.setZ(cur_map[(X, Y)]+10)

def generate_map_texture(map_tree, factor):
    map_world = map_tree.map3d
    size = map_world.size / factor
    image = PNMImage(size, size)
    #image.fill(0,0,0)
    for x in xrange(size):
        for y in xrange(size):
            px = x * factor
            py = y * factor
            if map_world[(px, py)] <= map_world.water_z:
                image.setPixel(x, y, (0, 0, 100))
            else:
                image.setPixel(x, y, (0, 100, 0))
    char_x, char_y, char_z = map_tree.coords
    char_x = char_x / factor
    char_y = char_y / factor
    if factor>2:
        image.setPixel(char_x, char_y, (255, 0, 0))
    else:
        for x in xrange(char_x - 1, char_x+2):
            cx = x
            if cx > size-1: cx = size-1
            if cx < 0: cx = 0
            for y in xrange(char_y - 1, char_y+2):
                cy = y
                if cy > size-1: cy = size-1
                if cy < 0: cy = 0
                image.setPixel(cx, cy, (255, 0, 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

