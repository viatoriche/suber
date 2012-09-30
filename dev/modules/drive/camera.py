# -*- coding: utf-8 -*-
import math

from config import Config
from direct.showbase import DirectObject
from pandac.PandaModules import Vec3, WindowProperties

class CamFree(DirectObject.DirectObject):
    config = Config()
    def __init__(self, game):
        base.disableMouse()

        self.game = game
        self.showterrain = game.world.show
        self.level = self.config.root_level
        self.high_level = self.config.root_level
        self.low_level = self.config.land_level
        base.camLens.setFar(20000)

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

        self.SpeedCam = 1
        self.SpeedRot = 0.05
        self.SpeedMult = 5

        self.CursorOffOn = 'On'

        self.props = WindowProperties()

        taskMgr.add(self.CamControl, 'CamControl')

    def setKey(self, key, value):
        self.keyMap[key] = value

    def CamSpeed(self, sd):
        self.SpeedCam *= sd

    def CamControl(self, task):
        if (self.keyMap["Mouse3"] != 0):
            if (self.CursorOffOn == 'On'):
                self.props.setCursorHidden(True)
                base.win.requestProperties(self.props)
                self.CursorOffOn = 'Off'

            dirFB = base.camera.getMat().getRow3(1)
            dirTT = base.camera.getMat().getRow3(2)
            dirRL = base.camera.getMat().getRow3(0)

            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            z = camera.getZ()

            Speed = self.SpeedCam

            if (self.keyMap["LSHIFT"]!=0):
                Speed = self.SpeedCam*self.SpeedMult
            if (self.keyMap["FORWARD"]!=0):
                camera.setPos(camera.getPos()+dirFB*Speed)
                #camera.setZ(z)
            if (self.keyMap["BACK"]!=0):
                camera.setPos(camera.getPos()-dirFB*Speed)
                #camera.setZ(z)
            if (self.keyMap["RIGHT"]!=0):
                camera.setPos(camera.getPos()+dirRL*Speed)
                #camera.setZ(z)
            if (self.keyMap["LEFT"]!=0):
                camera.setPos(camera.getPos()-dirRL*Speed)
                #camera.setZ(z)
            if (self.keyMap["UPWARDS"]!=0):
                camera.setZ(camera.getZ()+Speed)
            if (self.keyMap["DOWNWARDS"]!=0):
                camera.setZ(camera.getZ()-Speed)

            if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                camera.setH(camera.getH() -  (x - base.win.getXSize()/2)*self.SpeedRot)
                camera.setP(camera.getP() - (y - base.win.getYSize()/2)*self.SpeedRot)
                if (camera.getP()<=-90.1):
                    camera.setP(-90)
                if (camera.getP()>=90.1):
                    camera.setP(90)

            #print self.level
            self.showterrain()

        else:
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            base.win.requestProperties(self.props)

        return task.cont
