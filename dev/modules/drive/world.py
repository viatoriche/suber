#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
Drive module for World
"""

# Modificated for config modul

import sys, random
import time
import math

from modules.drive.landplane import Chank, LandNode
from modules.drive.shapeGenerator import Cube as CubeModel
from modules.drive.textures import textures
from modules.world.map3d import generate_heights
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage, PNMImage
from config import Config


class WaterNode():
    """Water plane for nya

    """
    def __init__(self, water_z):
        self.water_z = water_z

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

class MapTree():
    """Tree of Maps level
    """
    # map_tree ---
    map3d = None
    coords = (0, 0, 64)
    maps = {}
    config = Config()

    def __init__(self, game, parent = None, name = (0, 0)):
        self.parent = parent
        self.game = game
        self.name = name
        if self.parent:
            start_x, start_y = name
            self.gen_down_coords()
            print 'INIT: Name: ', name, ' / Parent name: ', self.parent.name, ' / level: ', self.game.world.level
            self.map3d = generate_heights(self, self.parent.map3d, start_x, start_y)

    def gen_down_coords(self):
        """Generate self.coords, when def down is run
        """
        x, y, z = self.parent.coords
        start_x, start_y = self.name
        cur_x = (x - (start_x * self.config.factor)) * self.config.factor
        cur_y = (y - (start_y * self.config.factor)) * self.config.factor
        self.coords = (cur_x, cur_y, 64)

    def down(self):
        """Create new MapTree and join
        """
        x, y, z = self.coords
        name = x / self.config.factor, y / self.config.factor
        return MapTree(self.game, self, name)

    def change_parent_coords(self):
        """Change parent coordinates when child is moving
        """
        if self.parent:
            cur_x, cur_y, cur_z = self.coords
            start_x, start_y = self.name
            x = (cur_x / self.config.factor) + (start_x * self.config.factor)
            y = (cur_y / self.config.factor) + (start_y * self.config.factor)
            self.parent.coords = (x, y, 64)
            #print 'Parent: ', self.parent.coords, ' self: ', self.coords

    def get_cache_map_height(self, mX, mY, X, Y):
        parentX, parentY = 0, 0
        nameX, nameY = mX, mY
        if nameX > self.config.factor_tor:
            nameX = nameX - self.config.factor
            parentX = 1
        elif nameX < 0:
            nameX = nameX + self.config.factor
            parentX = -1
        if nameY > self.config.factor_tor:
            nameY = nameY - self.config.factor
            parentY = 1
        elif nameY < 0:
            nameY = nameY + self.config.factor
            parentY = -1

        if not self.parent.parent:
            parentX, parentY = 0, 0

        #print 'Try get ', (mapX, mapY), (parentX, parentY), ' / ',nameX, nameY
        if self.maps != None and self.parent != None:
            if self.maps.has_key( (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ):

                return self.maps[ (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ].get((X, Y))
            else:
                return None


    def get_parent_map_height(self, mX, mY, X, Y):
        if not self.parent:
            return None

        parentX, parentY = 0, 0
        nameX, nameY = mX, mY
        if nameX > self.config.factor_tor:
            nameX = nameX - self.config.factor
            parentX = 1
        elif nameX < 0:
            nameX = nameX + self.config.factor
            parentX = -1
        if nameY > self.config.factor_tor:
            nameY = nameY - self.config.factor
            parentY = 1
        elif nameY < 0:
            nameY = nameY + self.config.factor
            parentY = -1

        if not self.parent.parent:
            parentX, parentY = 0, 0

        parent_map = self.parent.map3d
        if (parentX, parentY) != (0, 0):
            parent_map = self.parent.get_map(parentX, parentY, Join = False)


        x = (X / self.config.factor) + (nameX * self.config.factor)
        y = (Y / self.config.factor) + (nameY * self.config.factor)

        return parent_map[x, y]

    def change_cache_map_height(self, mX, mY, X, Y, height):
        parentX, parentY = 0, 0
        nameX, nameY = mX, mY
        if nameX > self.config.factor_tor:
            nameX = nameX - self.config.factor
            parentX = 1
        elif nameX < 0:
            nameX = nameX + self.config.factor
            parentX = -1
        if nameY > self.config.factor_tor:
            nameY = nameY - self.config.factor
            parentY = 1
        elif nameY < 0:
            nameY = nameY + self.config.factor
            parentY = -1

        if not self.parent.parent:
            parentX, parentY = 0, 0

        #print 'Try get ', (mapX, mapY), (parentX, parentY), ' / ',nameX, nameY
        if self.maps != None and self.parent != None:
            if self.maps.has_key( (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ):

                self.maps[ (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ][X, Y] = height
            else:
                def gen_map(source_map):
                    print self.name,'/',self.parent.name,' -> Start generate of map FOR CHANGE X.Y:', nameX, nameY
                    t = time.time()
                    return generate_heights(self, source_map, nameX, nameY, True, {(X, Y): height})

                if not self.parent.parent:
                    parentX, parentY = 0, 0

                source_map = self.parent.map3d
                parent_nameX = self.parent.name[0] + parentX
                parent_nameY = self.parent.name[1] + parentY
                if (parentX, parentY) != (0, 0):
                    print 'NEW PARENT FOR CHANGE MAP on ', self.game.world.level
                    new_source_map = self.parent.get_map(parentX, parentY, False)
                else:
                    new_source_map = source_map

                map3d = gen_map(new_source_map)
                self.maps[(parent_nameX, parent_nameY, nameX, nameY)] = map3d


    def get_cache_map_height(self, mX, mY, X, Y):
        parentX, parentY = 0, 0
        nameX, nameY = mX, mY
        if nameX > self.config.factor_tor:
            nameX = nameX - self.config.factor
            parentX = 1
        elif nameX < 0:
            nameX = nameX + self.config.factor
            parentX = -1
        if nameY > self.config.factor_tor:
            nameY = nameY - self.config.factor
            parentY = 1
        elif nameY < 0:
            nameY = nameY + self.config.factor
            parentY = -1

        if not self.parent.parent:
            parentX, parentY = 0, 0

        #print 'Try get ', (mapX, mapY), (parentX, parentY), ' / ',nameX, nameY
        if self.maps != None and self.parent != None:
            if self.maps.has_key( (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ):

                return self.maps[ (self.parent.name[0] + parentX,
                                   self.parent.name[1] + parentY,
                                   nameX, nameY) ].get((X, Y))
            else:
                return None


    # Oh, I love recurses :3
    def get_map(self, mapX, mapY, Join = False):
        """Get map for new name, and join to, if Join == True
        """
        #import pdb
        #pdb.set_trace()
        if (mapX, mapY) == (0, 0):
            return self.map3d

        if self.parent:
            nameX, nameY = self.name
            nameX, nameY = nameX + mapX, nameY + mapY


            parentX, parentY = 0, 0
            if nameX > self.config.factor_tor:
                nameX = nameX - self.config.factor
                parentX = 1
            elif nameX < 0:
                nameX = nameX + self.config.factor
                parentX = -1
            if nameY > self.config.factor_tor:
                nameY = nameY - self.config.factor
                parentY = 1
            elif nameY < 0:
                nameY = nameY + self.config.factor
                parentY = -1

            if Join:
                print self.name,'/',self.parent.name,' try Go X+', mapX, ' Y+', mapY,' -> ', nameX, nameY

            def gen_map(source_map):
                print self.name,'/',self.parent.name,' -> Start generate of map X.Y:', nameX, nameY
                t = time.time()
                map3d = generate_heights(self, source_map, nameX, nameY)
                print 'generate map:', time.time() - t
                return map3d

            if not self.parent.parent:
                parentX, parentY = 0, 0

            if self.maps.has_key( (self.parent.name[0]+parentX,
                                   self.parent.name[1]+parentY,
                                   nameX, nameY) ) and not Join:

                map3d = self.maps[ (self.parent.name[0]+parentX,
                                    self.parent.name[1]+parentY,
                                    nameX, nameY) ]

            else:

                source_map = self.parent.map3d
                parent_nameX = self.parent.name[0] + parentX
                parent_nameY = self.parent.name[1] + parentY
                if (parentX, parentY) != (0, 0):
                    print 'NEW PARENT on ', self.game.world.level, ' JOIN: ', Join
                    new_source_map = self.parent.get_map(parentX, parentY, Join = Join)
                else:
                    new_source_map = source_map

                if self.maps.has_key( (parent_nameX,
                                       parent_nameY,
                                       nameX, nameY) ):

                    map3d = self.maps[ (parent_nameX,
                                        parent_nameY,
                                        nameX, nameY) ]

                else:
                    map3d = gen_map(new_source_map)
                    self.maps[(parent_nameX, parent_nameY, nameX, nameY)] = map3d

            if Join:
                print self.name,' --> joined to: -->', nameX, nameY
                self.name = nameX, nameY
                self.map3d = map3d

            return map3d
        # If we are 1 lvl (high-end)
        else:
            return self.map3d

    def get_coords_txt(self, level, cam):
        cur_x, cur_y, cur_z = self.coords
        x, y, z = cam
        cam = int(x), int(y), int(z)

        try:
            cube_z = self.map3d[(cur_x, cur_y)]
        except TypeError:
            cube_z = 'unk'
            pass

        if self.parent:
            par_x, par_y, par_z = self.parent.coords
            return 'L:{8} * X: {0}, Y: {1} -> {2}:{3} * UX: {4}, UY: {5} -> {6}:{7} | cube = {9} | {10}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, par_x, par_y, par_x/16, par_y/16, level, cube_z, cam)
        else:
            return 'L:{4} * X: {0}, Y: {1} -> {2}:{3} | cube z = {5} | {6}'.format(
                cur_x, cur_y, cur_x/16, cur_y/16, level, cube_z, cam)


    #def up

class World():
    """
    docstring for World
    """
    map_2d = None
    # kawaii tech for LoD of World, logic Tree based
    map_tree = None
    # chanks {level: {(x, y): Chank}}, where x, y = X*mode_game, Y*mode_game with cubes
    chanks_map = {}
    config = Config()
    size_chank = config.factor
    # modelles with texture for cubes
    types = {}
    wayX, wayY = [], []
    def __init__(self):
        self.seed = random.randint(0, sys.maxint)
        self.chank_changed = True
        self.level = self.config.root_level
        self.new = True
        self.water_node = WaterNode(0.5)

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

        textures['sand'] = loader.loadTexture("res/textures/sand.png")
        textures['sand'].setMagfilter(Texture.FTLinearMipmapLinear)
        textures['sand'].setMinfilter(Texture.FTLinearMipmapLinear)

        self.water_node.create(0, 0, (self.config.factor_double,  self.config.factor_double))
        self.cube_size = 1
        self.cube_z = 10000

        self.types[land_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[land_mount_level].setTexture(textures[land_mount_level],1)

        self.types[low_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[low_mount_level].setTexture(textures[low_mount_level],1)

        self.types[mid_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[mid_mount_level].setTexture(textures[mid_mount_level],1)

        self.types[high_mount_level] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types[high_mount_level].setTexture(textures[high_mount_level],1)

        self.types['sand'] = CubeModel(self.cube_size, self.cube_size, self.cube_z)
        self.types['sand'].setTexture(textures['sand'],1)

        self.paint_thread = False

        for i in xrange(self.config.root_level,self.config.land_level+1):
            self.chanks_map[i] = {}

def show_terrain(game, cam_coords, level):
    if game.world.paint_thread:
        return

    def get_height(level, h):
        if h == 0:
            return 0
        high_level = abs(h)
        factor = game.config.factor
        mod = math.log(high_level, factor)
        return int((((level+1) ** mod) ** 2) / h)

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

        mode_double = game.config.factor_double
        mode_double_tor = game.config.factor_double_tor


        X = int(camX) / mode_double
        X = X * mode_double
        X = int(camX) - X

        Y = int(camY) / mode_double
        Y = Y * mode_double
        Y = int(camY) - Y

        Z = int(camZ)

        if [X] != game.world.wayX[-1:]:
            game.world.wayX.append(X)
        if [Y] != game.world.wayY[-1:]:
            game.world.wayY.append(Y)

        game.world.wayX = game.world.wayX[-2:]
        game.world.wayY = game.world.wayY[-2:]

        mapX, mapY = 0, 0

        # 63 --> 0 ---GO +1 ... 1 -> 0 --- GO -1

        if game.world.wayX == [63, 0]:
            mapX = +1

        if game.world.wayX == [0, 63]:
            mapX = -1

        if game.world.wayY == [63, 0]:
            mapY = +1

        if game.world.wayY == [0, 63]:
            mapY = -1

        if mapX != 0 or mapY != 0:
            game.world.wayX = []
            game.world.wayY = []
            game.world.map_tree.get_map(mapX, mapY, True)

        game.world.map_tree.coords = (X, Y, Z)
        game.world.map_tree.change_parent_coords()
        game.write(game.world.map_tree.get_coords_txt(level, cam_coords))

    # down / up
    else:
        for ch in game.world.chanks_map[last_level]:
            game.world.chanks_map[last_level][ch].destroy()

        game.world.chanks_map[last_level] = {}

        game.world.chank_changed = True

        if level > last_level:
            game.world.map_tree = game.world.map_tree.down()
        if level < last_level:
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

    game.cmd_handle('showmap')
    if (lastX, lastY) != (X, Y):
        OK = True

    if not OK:
        return

    cur_map = game.world.map_tree.map3d
    if (X / size_chank, Y / size_chank) != (lastX / size_chank, lastY / size_chank):
        for ch in game.world.chanks_map[level].values():
            ch.hide()
        game.world.chank_changed = True


    if not game.world.chank_changed:
        return


    def Paint():
        """Create cubes on screen
        """

        mode = game.config.factor
        mode_double = game.config.factor_double
        mode_tor = game.config.factor_tor
        mode_double_tor = game.config.factor_double_tor

        t= time.time()

        cube_size = game.world.cube_size
        types = game.world.types

        chanks = game.config.count_chanks

        dx = ((X / size_chank) - chanks) * size_chank
        for xcount in xrange(chanks * 2):
            dy = ((Y / size_chank) - chanks) * size_chank
            for ycount in xrange(chanks * 2):
                chank_X = dx + (mode_double * (int(camX)/mode_double))
                chank_Y = dy + (mode_double * (int(camY)/mode_double))
                water_X = chank_X - (mode*mode) - (mode*(chanks/2))
                water_Y = chank_Y - (mode*mode) - (mode*(chanks/2))
                game.world.water_node.reset(water_X, water_Y)

                cubes = {}
                time_gen = time.time()
                for x in xrange(dx, dx + size_chank):
                    mapX = 0
                    cX = x
                    if cX < 0:
                        cX = mode_double+cX
                        mapX = -1
                    if cX > mode_double_tor:
                        cX = cX - mode_double
                        mapX = 1
                    for y in xrange(dy, dy + size_chank):
                        mapY = 0
                        cY = y
                        if cY < 0:
                            cY = mode_double + cY
                            mapY = -1
                        if cY > mode_double_tor:
                            cY = cY-mode_double
                            mapY = 1

                        if (mapX, mapY) != (0, 0):
                            cur_map = game.world.map_tree.get_map(mapX, mapY, False)
                        else:
                            cur_map = game.world.map_tree.map3d

                        cube_X = x + (mode_double * (int(camX)/mode_double))
                        cube_Y = y + (mode_double * (int(camY)/mode_double))
                        cube_X = cube_X * cube_size
                        cube_Y = cube_Y * cube_size

                        height = get_height(level, cur_map[(cX, cY)])
                        if cur_map[(cX, cY)]<=cur_map.water_z:
                            cubes[(cube_X, cube_Y, height - game.world.cube_z)] = 'sand'
                        else:
                            if height <= cur_map.water_z:
                                height = cur_map.water_z + 1
                            if cur_map[(cX, cY)] in range(game.config.land_mount_level[0], game.config.land_mount_level[1]+1):
                                cubes[(cube_X, cube_Y, height - game.world.cube_z)] = game.config.land_mount_level

                            elif cur_map[(cX, cY)] in range(game.config.low_mount_level[0], game.config.low_mount_level[1]+1):
                                cubes[(cube_X, cube_Y, height - game.world.cube_z)] = game.config.low_mount_level

                            elif cur_map[(cX, cY)] in range(game.config.mid_mount_level[0], game.config.mid_mount_level[1]+1):
                                cubes[(cube_X, cube_Y, height - game.world.cube_z)] = game.config.mid_mount_level

                            else:
                                cubes[(cube_X, cube_Y, height - game.world.cube_z)] = game.config.high_mount_level


                #print 'time gen cubes: ', time.time() - time_gen

                #time_create = time.time()
                if game.world.chanks_map[level].has_key((chank_X, chank_Y)) and\
                      game.world.chanks_map[level][(chank_X, chank_Y)].cubes == cubes:
                        game.world.chanks_map[level][(chank_X, chank_Y)].show()
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
        base.camera.setZ(get_height(level, cur_map[(X, Y)])+16)

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
    image.setPixel(char_x, char_y, (255, 0, 0))
    #if factor>2:
        #image.setPixel(char_x, char_y, (255, 0, 0))
    #else:
        #for x in xrange(char_x - 1, char_x+2):
            #cx = x
            #if cx > size-1: cx = size-1
            #if cx < 0: cx = 0
            #for y in xrange(char_y - 1, char_y+2):
                #cy = y
                #if cy > size-1: cy = size-1
                #if cy < 0: cy = 0
                #image.setPixel(cx, cy, (255, 0, 0))
    texture = Texture()
    texture.load(image)
    return texture
# vi: ft=python:tw=0:ts=4

