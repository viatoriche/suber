# -*- coding: utf-8 -*-
import math
import time
import random, sys, os

from panda3d.core import CompassEffect
from config import Config
from direct.showbase import DirectObject
from panda3d.core import TPHigh, TPUrgent
from pandac.PandaModules import Vec3, VBase3, WindowProperties
from panda3d.core import CollisionNode, GeomNode, CollisionSphere
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from voxplanet.support import profile_decorator

class HotKeys(DirectObject.DirectObject):
    config = Config()
    def __init__(self, gui):
        self.gui = gui
        self.accept("f12", self.toggle_wire_texture)
        self.accept("f11", self.toggle_wire_frame)

    def toggle_wire_frame(self):
        self.gui.toggleWireframe()

    def toggle_wire_texture(self):
        self.gui.toggleTexture()

class GlobalMap(DirectObject.DirectObject):
    config = Config()
    def __init__(self, game):
        self.game = game
        self.image = None
        self.distanceScale = self.game.world.config.size_world / 2
        self.game.gui.hotkeys.accept('mouse1', self.focusCameraOnMouse)

    def focusCameraOnMouse(self, z = 0, distance = 40):
        """Moves the camera so that it is looking at the spot on the minimap where the mouse is.
        If the mouse is not over the minimap, do nothing.
        z = the z coordinate of the point you want to look at (the x and y coordinates are defined by where
            the mouse is relative to the minimap)
        distance = how far away you want the camera to be from the point its looking at
        """
        if self.image == None:
            return

        x = self.game.gui.mouseWatcherNode.getMouseX()
        y = self.game.gui.mouseWatcherNode.getMouseY()
        mapX, mapZ, mapY = self.screenToMinimapCoordinates(x, y)

        if self._between(mapX,-1,1) and self._between(mapY,-1,1): #if mouse click was on the minimap..
            focusPoint = self.screenToWorldCoordinates( mapX, mapY )
            self.game.cmd_handler.cmd_teleport([focusPoint[0], focusPoint[1]])
            self.game.cmd_handler.cmd_hide_map()

    def screenToMinimapCoordinates(self, x, y):
        """Given a position on the screen, return the position relative to Minimap.root
        """
        mouseNP = render2d.attachNewNode("mouseNP")
        mouseNP.setPos(x,0,y)

        output = mouseNP.getPos(self.image)
        mouseNP.removeNode()

        return output

    def _between(self, x, a, b):
        "A small utility function."
        return ( (a <= x <= b) or (b <= x <= a) )

    def screenToWorldCoordinates(self, x, y):
        dx = self.distanceScale * x
        dy = -self.distanceScale * y
        return self.distanceScale + dx, self.distanceScale + dy

class CollisionAvatar():
    """Collision for avatar
    """
    def __init__(self, game):
        self.game = game
        self.enable = False
        self.camera = self.game.gui.camera
        self.debug = False

        self.sphere_node = CollisionNode('Sphere')
        self.sphere_nodepath = self.game.world.avatar.attachNewNode(self.sphere_node)
        self.sphere_node.setFromCollideMask(BitMask32.bit(2))
        self.sphere_node.setIntoCollideMask(BitMask32.bit(4))
        self.sphere = CollisionSphere(0, 0, 0.5, 0.5)
        self.sphere_node.addSolid(self.sphere)
        self.sphere_handler = CollisionHandlerQueue()

        self.ray_node = CollisionNode('downRay')
        self.ray_nodepath = self.game.world.avatar.attachNewNode(self.ray_node)
        self.ray_node.setFromCollideMask(BitMask32.bit(1))
        self.ray_node.setIntoCollideMask(BitMask32.bit(3))
        self.ray = CollisionRay()
        self.ray.setOrigin(0, 0, 5)
        self.ray.setDirection(0, 0, -1)
        self.ray_node.addSolid(self.ray)
        self.ray_handler = CollisionHandlerQueue()

    def set_debug(self, value):
        """docstring for debug
        """
        self.debug = value
        if self.debug:
            self.ray_nodepath.show()
            self.sphere_nodepath.show()
        else:
            self.ray_nodepath.hide()
            self.sphere_nodepath.hide()

    def set_enable(self, value, Fly = True):
        self.enable = value
        self.fly = Fly
        if self.enable:
            self.game.gui.cTrav.addCollider(self.ray_nodepath, self.ray_handler)
            self.game.gui.cTrav.addCollider(self.sphere_nodepath, self.sphere_handler)
        else:
            self.game.gui.cTrav.removeCollider(self.ray_nodepath)
            self.game.gui.cTrav.removeCollider(self.sphere_nodepath)

    def detector(self):
        if not self.enable:
            return

        self.game.gui.cTrav.traverse(self.game.world.root_node)

        if self.sphere_handler.getNumEntries() > 0:
            #self.sphere_handler.sortEntries()
            self.game.world.avatar.setPos(self.game.world.root_node, self.lastpos)

        if self.ray_handler.getNumEntries() > 0:
            self.ray_handler.sortEntries()
            pickedObj = self.ray_handler.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag('Chunk')
            if not pickedObj.isEmpty():
                Z = self.ray_handler.getEntry(0).\
                                            getSurfacePoint(self.game.world.root_node).getZ()
                if self.fly:
                    if Z > self.game.world.avatar.getZ(self.game.world.root_node):
                        self.game.world.avatar.setZ(self.game.world.root_node, Z)
                else:
                    self.game.world.avatar.setZ(self.game.world.root_node, Z)



class MoveAvatar(DirectObject.DirectObject):
    """Free fly avatar
    game - modules.main.Main()
    root_node - root render for game
    """
    def __init__(self, game):
        self.game = game
        self.SpeedCam = 0.05
        self.sleep = 0.01
        self.fly_mod = 0.01
        self.SpeedMult = 3
        self.isMoving = False
        self.fly = True
        self.CursorOffOn = 'On'
        taskMgr.setupTaskChain('avatar_move', numThreads = 1,
                       frameSync = False, threadPriority = TPUrgent, timeslicePriority = False)
        self.props = WindowProperties()


    def set_key(self, key, value):
        self.keyMap[key] = value

    def set_enable(self, value, Fly = True):
        self.enable = value
        self.fly = Fly

        self.root_node = self.game.world.root_node
        self.avatar = self.game.world.avatar
        self.hotkeys = self.game.gui.hotkeys

        if self.enable:
            self.game.gui.disableMouse()
            self.keyMap = {"FORWARD":0, "BACK":0, "RIGHT":0,
                           "LEFT":0, "Mouse3":0, "LSHIFT":0,
                           "UPWARDS":0, "DOWNWARDS":0}

            self.hotkeys.accept("w", self.set_key, ["FORWARD",1])
            self.hotkeys.accept("w-up", self.set_key, ["FORWARD",0])
            self.hotkeys.accept("s", self.set_key, ["BACK",1])
            self.hotkeys.accept("s-up", self.set_key, ["BACK",0])
            self.hotkeys.accept("d", self.set_key, ["RIGHT",1])
            self.hotkeys.accept("d-up", self.set_key, ["RIGHT",0])
            self.hotkeys.accept("a", self.set_key, ["LEFT",1])
            self.hotkeys.accept("a-up", self.set_key, ["LEFT",0])
            self.hotkeys.accept("q", self.set_key, ["UPWARDS",1])
            self.hotkeys.accept("q-up", self.set_key, ["UPWARDS",0])
            self.hotkeys.accept("e", self.set_key, ["DOWNWARDS",1])
            self.hotkeys.accept("e-up", self.set_key, ["DOWNWARDS",0])
            self.hotkeys.accept("lshift", self.set_key, ["LSHIFT",1])
            self.hotkeys.accept("lshift-up", self.set_key, ["LSHIFT",0])

            taskMgr.add(self.avatar_control, 'CamControl', taskChain = 'avatar_move')
        else:
            self.game.gui.enableMouse()

    def avatar_control(self, task):
        """Task for controlling of self.avatar
        """
        if not self.enable:
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            self.game.gui.win.requestProperties(self.props)
            return task.done


            #self.game.world.mutex_repaint.acquire()
        if (self.CursorOffOn == 'On'):
            self.props.setCursorHidden(True)
            self.game.gui.win.requestProperties(self.props)
            self.CursorOffOn = 'Off'

        self.game.collision_avatar.lastpos = self.avatar.getPos(self.root_node)

        z = self.avatar.getZ(self.root_node)

        fly_spd = abs(z - self.game.world.chunks_map.land_z) * self.fly_mod
        #
        Speed = (self.SpeedCam + fly_spd)

        avatar_run = False

        if (self.keyMap["LSHIFT"]!=0):
            Speed = (self.SpeedCam + fly_spd) * self.SpeedMult

        if (self.keyMap["FORWARD"]!=0):
            avatar_run = True
            self.avatar.setY(self.avatar, Speed)
        if (self.keyMap["BACK"]!=0):
            avatar_run = True
            self.avatar.setY(self.avatar, -Speed)
        if (self.keyMap["RIGHT"]!=0):
            avatar_run = True
            self.avatar.setX(self.avatar, Speed)
        if (self.keyMap["LEFT"]!=0):
            avatar_run = True
            self.avatar.setX(self.avatar, -Speed)

        if (self.keyMap["UPWARDS"]!=0):
            if self.fly:
                avatar_run = True
                self.avatar.setZ(self.avatar, Speed)
        if (self.keyMap["DOWNWARDS"]!=0):
            if self.fly:
                avatar_run = True
                self.avatar.setZ(self.avatar, -Speed)

        #if self.avatar.getZ(self.game.world.root_node) < self.game.world.chunks_map.land_z-5:
            #self.avatar.setZ(self.game.world.root_node, self.game.world.chunks_map.land_z)

        if avatar_run:
            if not self.isMoving:
                self.game.char.loop('run')
                self.isMoving = True
        else:
            self.game.char.stop()
            self.game.char.pose('walk', 5)
            self.isMoving = False

        self.game.collision_avatar.detector()
        time.sleep(self.sleep)

        return task.cont

class CamManager(DirectObject.DirectObject):
    """1st or 3d person camera, or disable
    """
    def __init__(self, game):
        self.game = game
        self.char = self.game.char
        self.win = self.game.gui.win
        self.hotkeys = self.game.gui.hotkeys
        self.node = NodePath('char')
        self.Ccentr = NodePath('Ccentr')
        self.Ccentr.reparentTo(self.node)
        self.Ccentr.setZ(1)
        self.third_dist = -6
        self.sleep = 0.001
        self.camera = self.game.gui.camera
        self.char.reparentTo(self.node)
        taskMgr.setupTaskChain('cam_move', numThreads = 1,
                       frameSync = False, threadPriority = TPUrgent, timeslicePriority = False)


    def set_enable(self, value, third = False):
        self.enable = value
        self.third = third

        self.node.reparentTo(self.game.world.root_node)
        self.node.setPos(self.game.world.avatar.getPos())
        if self.enable:
            self.camera.reparentTo(self.Ccentr)
            if self.third:
                self.camera.setPos(0, self.third_dist, 0)
                #self.char.show()
            else:
                self.camera.setPos(0, 0, 0)
                #self.char.hide()
            self.camera.lookAt(self.Ccentr)
            taskMgr.add(self.mouse_update, 'mouse-task')
        else:
            self.camera.reparentTo(self.game.world.root_node)
            self.camera.setPos(self.game.world.root_node, self.game.world.avatar.getPos(self.game.world.root_node))
            self.node.detachNode()

    #@profile_decorator
    def mouse_update(self, task):
        """ this task updates the mouse """
        if not self.enable:
            return task.done

        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, self.win.getXSize()/2, self.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - self.win.getXSize()/2)*0.1)
            self.Ccentr.setP(self.Ccentr.getP() - (y - self.win.getYSize()/2)*0.1)

        time.sleep(self.sleep)
        return task.cont

    def point_dist(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)
