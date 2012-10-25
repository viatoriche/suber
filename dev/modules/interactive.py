# -*- coding: utf-8 -*-
import math
import time
import random, sys, os

from panda3d.core import CompassEffect
from config import Config
from direct.showbase import DirectObject
from panda3d.core import TPNormal
from pandac.PandaModules import Vec3, VBase3, WindowProperties
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32

class HotKeys(DirectObject.DirectObject):
    config = Config()
    def __init__(self, gui):
        self.gui = gui
        self.gui.disableMouse()
        self.accept("x", self.toggle_wire)

    def toggle_wire(self):
        self.gui.toggleWireframe()
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


class CamFreeMgr(DirectObject.DirectObject):
    """Free fly camera

    game - modules.main.Main()
    root_node - root render for game
    """
    def __init__(self, game):
        self.game = game
        self.SpeedRot = 0.05
        self.SpeedMult = 10
        self.delay = 0.02

        self.props = WindowProperties()

        #taskMgr.setupTaskChain('camera_chain', numThreads = 1,
                       #threadPriority = TPNormal, frameSync = False)


    def set_key(self, key, value):
        self.keyMap[key] = value

    def cam_speed(self, sd):
        self.SpeedCam *= sd

    def set_enable(self, value):
        self.enable = value

        self.root_node = self.game.world.root_node
        self.camera = self.game.gui.camera
        self.hotkeys = self.game.gui.hotkeys

        if self.enable:
            self.CursorOffOn = 'On'
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
            self.hotkeys.accept("mouse3", self.set_key, ["Mouse3",1])
            self.hotkeys.accept("mouse3-up", self.set_key, ["Mouse3",0])
            self.hotkeys.accept("lshift", self.set_key, ["LSHIFT",1])
            self.hotkeys.accept("lshift-up", self.set_key, ["LSHIFT",0])
            self.hotkeys.accept("wheel_up", self.cam_speed, [1.1])
            self.hotkeys.accept("wheel_down", self.cam_speed, [0.9])

            self.camera.reparentTo(self.root_node)
            taskMgr.doMethodLater(self.delay, self.cam_control, 'CamControl')

    def cam_control(self, task):
        """Task for controlling of camera
        """
        if not self.enable:
            return task.done


        if (self.keyMap["Mouse3"] != 0):
            #self.game.world.mutex_repaint.acquire()
            if (self.CursorOffOn == 'On'):
                self.props.setCursorHidden(True)
                self.game.gui.win.requestProperties(self.props)
                self.CursorOffOn = 'Off'

            dirFB = self.game.gui.camera.getMat(self.root_node).getRow3(1)
            dirRL = self.game.gui.camera.getMat(self.root_node).getRow3(0)

            d = 1000 * globalClock.getDt()

            md = self.game.gui.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            z = camera.getZ(self.root_node)

            real_z = (z - self.game.world.chunks_map.land_z)

            spd = real_z * self.delay



            self.SpeedCam = spd + self.delay + (2*globalClock.getDt())
            Speed = self.SpeedCam

            if (self.keyMap["LSHIFT"]!=0):
                Speed = self.SpeedCam*self.SpeedMult
            if (self.keyMap["FORWARD"]!=0):
                camera.setPos(self.root_node, camera.getPos(self.root_node)+dirFB*Speed)
                #self.root_node.setPos(self.root_node.getPos()-dirFB*Speed)
                #camera.setZ(z)
            if (self.keyMap["BACK"]!=0):
                camera.setPos(self.root_node, camera.getPos(self.root_node)-dirFB*Speed)
                #self.root_node.setPos(self.root_node.getPos()+dirFB*Speed)
                #camera.setZ(z)
            if (self.keyMap["RIGHT"]!=0):
                camera.setPos(self.root_node, camera.getPos(self.root_node)+dirRL*Speed)
                #self.root_node.setPos(self.root_node.getPos()-dirRL*Speed)
                #camera.setZ(z)
            if (self.keyMap["LEFT"]!=0):
                camera.setPos(self.root_node, camera.getPos(self.root_node)-dirRL*Speed)
                #self.root_node.setPos(self.root_node.getPos()+dirRL*Speed)
                #camera.setZ(z)
            if (self.keyMap["UPWARDS"]!=0):
                camera.setZ(self.root_node, camera.getZ(self.root_node)+Speed)
                #self.root_node.setZ(self.root_node.getZ()-Speed)
            if (self.keyMap["DOWNWARDS"]!=0):
                camera.setZ(self.root_node, camera.getZ(self.root_node)-Speed)
                #self.root_node.setZ(self.root_node.getZ()+Speed)

            if self.game.gui.win.movePointer(0, self.game.gui.win.getXSize()/2,
                                             self.game.gui.win.getYSize()/2):
                self.camera.setH(self.root_node,
                                 self.camera.getH(self.root_node) -\
                                 (x - self.game.gui.win.getXSize()/2)*self.SpeedRot)
                self.camera.setP(self.root_node,
                                 self.camera.getP(self.root_node) -\
                                 (y - self.game.gui.win.getYSize()/2)*self.SpeedRot)
                if (self.camera.getP(self.root_node)<=-90.1):
                    self.camera.setP(self.root_node, -90)
                if (self.camera.getP(self.root_node)>=90.1):
                    self.camera.setP(self.root_node, 90)

        else:
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            self.game.gui.win.requestProperties(self.props)

        return task.again

class TPCamMgr(DirectObject.DirectObject):
    def __init__(self, game):
        self.game = game
        self.char = self.game.char
        self.win = self.game.gui.win
        self.hotkeys = self.game.gui.hotkeys
        self.node = NodePath('char')
        self.Ccentr = NodePath('Ccentr')
        self.Ccentr.reparentTo(self.node)
        self.Ccentr.setZ(1)
        self.camera = self.game.gui.camera
        self.char.reparentTo(self.node)

    def set_enable(self, value, dist):
        self.enable = value
        self.dist = dist

        self.node.reparentTo(self.game.world.root_node)
        self.node.setPos(self.game.world.avatar.getPos())
        if self.enable:
            self.camera.reparentTo(self.Ccentr)
            self.camera.setPos(0, self.dist, 0)
            self.camera.lookAt(self.Ccentr)
            taskMgr.add(self.mouseUpdate, 'mouse-task')
        else:
            self.camera.reparentTo(self.game.world.root_node)
            self.camera.setPos(self.node.getPos())
            self.node.detachNode()

        print 'Ccentr, node, camera, char'
        print self.Ccentr.getPos(), self.node.getPos(), self.camera.getPos(), self.char.getPos()
        print self.Ccentr.getPos(self.game.world.root_node), self.node.getPos(self.game.world.root_node), self.camera.getPos(self.game.world.root_node), self.char.getPos(self.game.world.root_node)

    def mouseUpdate(self,task):
        """ this task updates the mouse """
        if not self.enable:
            return task.done

        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, self.win.getXSize()/2, self.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - self.win.getXSize()/2)*0.1)
            self.Ccentr.setP(self.Ccentr.getP() - (y - self.win.getYSize()/2)*0.1)
        return task.cont

    def point_dist(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)
