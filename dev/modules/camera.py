# -*- coding: utf-8 -*-
import math
import time

from config import Config
from direct.showbase import DirectObject
from panda3d.core import TPNormal
from pandac.PandaModules import Vec3, WindowProperties

class CamFree(DirectObject.DirectObject):
    """Free fly camera

    game - modules.main.Main()
    root_node - root render for game
    """
    config = Config()
    def __init__(self, game, root_node = None):
        base.disableMouse()

        self.game = game
        if root_node == None:
            self.root_node = render
        else:
            self.root_node = root_node

        self.keyMap = {"FORWARD":0, "BACK":0, "RIGHT":0,
                       "LEFT":0, "Mouse3":0, "LSHIFT":0,
                       "UPWARDS":0, "DOWNWARDS":0}
        self.accept("w", self.setKey, ["FORWARD",1])
        self.accept("w-up", self.setKey, ["FORWARD",0])
        self.accept("s", self.setKey, ["BACK",1])
        self.accept("s-up", self.setKey, ["BACK",0])
        self.accept("d", self.setKey, ["RIGHT",1])
        self.accept("d-up", self.setKey, ["RIGHT",0])
        self.accept("a", self.setKey, ["LEFT",1])
        self.accept("a-up", self.setKey, ["LEFT",0])
        self.accept("q", self.setKey, ["UPWARDS",1])
        self.accept("q-up", self.setKey, ["UPWARDS",0])
        self.accept("e", self.setKey, ["DOWNWARDS",1])
        self.accept("e-up", self.setKey, ["DOWNWARDS",0])
        self.accept("mouse3", self.setKey, ["Mouse3",1])
        self.accept("mouse3-up", self.setKey, ["Mouse3",0])
        self.accept("lshift", self.setKey, ["LSHIFT",1])
        self.accept("lshift-up", self.setKey, ["LSHIFT",0])
        self.accept("wheel_up", self.CamSpeed, [1.1])
        self.accept("wheel_down", self.CamSpeed, [0.9])

        self.SpeedRot = 0.05
        self.SpeedMult = 10

        self.CursorOffOn = 'On'

        self.props = WindowProperties()

        taskMgr.setupTaskChain('camera_chain', numThreads = 1, tickClock = False,
                       threadPriority = TPNormal, frameSync = False)

        taskMgr.doMethodLater(0.01, self.CamControl, 'CamControl')

    def setKey(self, key, value):
        self.keyMap[key] = value

    def CamSpeed(self, sd):
        self.SpeedCam *= sd

    def CamControl(self, task):
        """Task for controlling of camera
        """
        if (self.keyMap["Mouse3"] != 0):
            #self.game.world.mutex_repaint.acquire()
            if (self.CursorOffOn == 'On'):
                self.props.setCursorHidden(True)
                base.win.requestProperties(self.props)
                self.CursorOffOn = 'Off'

            dirFB = base.camera.getMat(self.root_node).getRow3(1)
            dirTT = base.camera.getMat(self.root_node).getRow3(2)
            dirRL = base.camera.getMat(self.root_node).getRow3(0)

            self.SpeedCam = camera.getZ(self.root_node)*0.001
            if self.SpeedCam < 0.01:
                self.SpeedCam = 0.01

            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            z = camera.getZ(self.root_node)

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

            if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                camera.setH(self.root_node, camera.getH(self.root_node) -  (x - base.win.getXSize()/2)*self.SpeedRot)
                camera.setP(self.root_node, camera.getP(self.root_node) - (y - base.win.getYSize()/2)*self.SpeedRot)
                if (camera.getP(self.root_node)<=-90.1):
                    camera.setP(self.root_node, -90)
                if (camera.getP(self.root_node)>=90.1):
                    camera.setP(self.root_node, 90)

            #self.game.world.mutex_repaint.release()

            #print self.level
            #self.showterrain()

        else:
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            base.win.requestProperties(self.props)

        #time.sleep(0.1)
        return task.again
