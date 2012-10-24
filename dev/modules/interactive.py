# -*- coding: utf-8 -*-
import math
import time
import random, sys, os

from panda3d.core import CompassEffect
from config import Config
from direct.showbase import DirectObject
from panda3d.core import TPNormal
from pandac.PandaModules import Vec3, WindowProperties
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


class CamFree():
    """Free fly camera

    game - modules.main.Main()
    root_node - root render for game
    """
    config = Config()
    def __init__(self, game, root_node = None):
        self.game = game
        if root_node == None:
            self.root_node = render
        else:
            self.root_node = root_node

        self.SpeedRot = 0.05
        self.SpeedMult = 10
        self.delay = 0.02

        self.props = WindowProperties()

        self.set_enable(True)

        #taskMgr.setupTaskChain('camera_chain', numThreads = 1,
                       #threadPriority = TPNormal, frameSync = False)

        taskMgr.doMethodLater(self.delay, self.cam_control, 'CamControl')

    def set_key(self, key, value):
        self.keyMap[key] = value

    def cam_speed(self, sd):
        self.SpeedCam *= sd

    def __getattr__(self, attr, *args, **params):
        return eval('self.game.gui.camera.{0}(*args, **params)'.format(attr))

    def set_enable(self, value):
        self.CursorOffOn = 'On'
        self.keyMap = {"FORWARD":0, "BACK":0, "RIGHT":0,
                       "LEFT":0, "Mouse3":0, "LSHIFT":0,
                       "UPWARDS":0, "DOWNWARDS":0}

        self.game.gui.hotkeys.accept("w", self.set_key, ["FORWARD",1])
        self.game.gui.hotkeys.accept("w-up", self.set_key, ["FORWARD",0])
        self.game.gui.hotkeys.accept("s", self.set_key, ["BACK",1])
        self.game.gui.hotkeys.accept("s-up", self.set_key, ["BACK",0])
        self.game.gui.hotkeys.accept("d", self.set_key, ["RIGHT",1])
        self.game.gui.hotkeys.accept("d-up", self.set_key, ["RIGHT",0])
        self.game.gui.hotkeys.accept("a", self.set_key, ["LEFT",1])
        self.game.gui.hotkeys.accept("a-up", self.set_key, ["LEFT",0])
        self.game.gui.hotkeys.accept("q", self.set_key, ["UPWARDS",1])
        self.game.gui.hotkeys.accept("q-up", self.set_key, ["UPWARDS",0])
        self.game.gui.hotkeys.accept("e", self.set_key, ["DOWNWARDS",1])
        self.game.gui.hotkeys.accept("e-up", self.set_key, ["DOWNWARDS",0])
        self.game.gui.hotkeys.accept("mouse3", self.set_key, ["Mouse3",1])
        self.game.gui.hotkeys.accept("mouse3-up", self.set_key, ["Mouse3",0])
        self.game.gui.hotkeys.accept("lshift", self.set_key, ["LSHIFT",1])
        self.game.gui.hotkeys.accept("lshift-up", self.set_key, ["LSHIFT",0])
        self.game.gui.hotkeys.accept("wheel_up", self.cam_speed, [1.1])
        self.game.gui.hotkeys.accept("wheel_down", self.cam_speed, [0.9])

        self.enable = value

    def cam_control(self, task):
        """Task for controlling of camera
        """
        if not self.enable:
            return task.again


        if (self.keyMap["Mouse3"] != 0):
            #self.game.world.mutex_repaint.acquire()
            if (self.CursorOffOn == 'On'):
                self.props.setCursorHidden(True)
                self.game.gui.win.requestProperties(self.props)
                self.CursorOffOn = 'Off'

            dirFB = self.game.gui.camera.getMat(self.root_node).getRow3(1)
            dirTT = self.game.gui.camera.getMat(self.root_node).getRow3(2)
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

            if self.game.gui.win.movePointer(0, self.game.gui.win.getXSize()/2, self.game.gui.win.getYSize()/2):
                self.game.gui.camera.setH(self.root_node, self.game.gui.camera.getH(self.root_node) -  (x - self.game.gui.win.getXSize()/2)*self.SpeedRot)
                self.game.gui.camera.setP(self.root_node, self.game.gui.camera.getP(self.root_node) - (y - self.game.gui.win.getYSize()/2)*self.SpeedRot)
                if (self.game.gui.camera.getP(self.root_node)<=-90.1):
                    self.game.gui.camera.setP(self.root_node, -90)
                if (self.game.gui.camera.getP(self.root_node)>=90.1):
                    self.game.gui.camera.setP(self.root_node, 90)

        else:
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            self.game.gui.win.requestProperties(self.props)

        #time.sleep(0.1)
        return task.again

class TPCam():
    def __init__(self, game, near = 5., far = 2000., dist = 30.,
                 step = 20., heading = -30., pitch = -45., ms = 0.3,
                 slowness = 30., linear = False):

        self.game = game
        self.target = self.game.char
        self.near = near
        self.far = far
        self.dist = dist
        self.step = step
        self.heading = heading
        self.pitch = pitch
        self.mouse_sensitivity = ms
        self.slowness = slowness
        self.linear = linear
        self.dragging = False
        self.enable = False

        taskMgr.add(self.update, 'camera.update')

        self.parent = render.attachNewNode('parent')
        self.parent.reparentTo(self.target)
        self.parent.setEffect(CompassEffect.make(render))
        base.camera.reparentTo(self.parent)
        base.camera.lookAt(self.parent)
        base.camera.setY(-self.dist)

    def set_enable(self, value):
        self.enable = value
        self.game.gui.disableMouse()
        self.game.gui.hotkeys.accept('wheel_up', self.wheel_up)
        self.game.gui.hotkeys.accept('wheel_down', self.wheel_down)
        self.game.gui.hotkeys.accept('mouse3', self.start_drag)
        self.game.gui.hotkeys.accept('mouse3-up', self.stop_drag)
        if self.enable:
            self.target.reparentTo(self.game.gui.render)
        else:
            self.target.detachNode()

    def wheel_up(self):
        if not self.enable:
            return
        if self.linear:
            self.dist = self.dist - self.step
        else:
            self.dist = self.dist / 2
        if self.dist < self.near:
            self.dist = self.near

    def wheel_down(self):
        if not self.enable:
            return
        if self.linear:
            self.dist = self.dist + self.step
        else:
            self.dist = self.dist * 2
        if self.dist > self.far:
            self.dist = self.far

    def __getattr__(self, attr, *args, **params):
        if not self.enable:
            return
        print attr, args, params
        return eval('self.target.{0}(*args, **params)'.format(attr))

    def start_drag(self):
        if not self.enable:
            return
        self.dragging = True
        md = base.win.getPointer(0)
        self.mx = md.getX()
        self.my = md.getY()

    def stop_drag(self):
        if not self.enable:
            return
        md = base.win.getPointer(0)
        mx = (self.mx - md.getX())*self.mouse_sensitivity
        my = (self.my - md.getY())*self.mouse_sensitivity
        self.heading = self.heading + mx
        self.pitch = self.pitch + my
        self.dragging = False

    def update(self, task):
        if not self.enable:
            return task.cont

        if self.dragging:
            md = base.win.getPointer(0)
            mx = (self.mx - md.getX())*self.mouse_sensitivity
            my = (self.my - md.getY())*self.mouse_sensitivity
            self.parent.setHpr(self.heading + mx, self.pitch + my, 0)
        else:
            self.parent.setHpr(self.heading, self.pitch, 0)

        camdist = base.camera.getDistance(self.target)
        delta = self.dist - camdist
        delta = delta / self.slowness
        curdist = camdist + delta
        base.camera.setY(-curdist)

        return task.cont

class CharCam():
    def __init__(self, game):
        self.game = game
        self.game.gui.disableMouse()
        self.char = self.game.char
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        self.isMoving = False
        self.isDebug = False
        self.SpeedRot = 0.05
        self.head = NodePath(PandaNode("head"))
        self.head.reparentTo(render)
        taskMgr.add(self.move, "moveTask")

    def __getattr__(self, attr, *args, **params):
        print attr, args, params
        return eval('self.char.{0}(*args, **params)'.format(attr))

    def set_enable(self, value):
        self.enable = value

        self.game.gui.hotkeys.accept("arrow_left", self.setKey, ["left",1])
        self.game.gui.hotkeys.accept("arrow_right", self.setKey, ["right",1])
        self.game.gui.hotkeys.accept("arrow_up", self.setKey, ["forward",1])
        self.game.gui.hotkeys.accept("a", self.setKey, ["cam-left",1])
        self.game.gui.hotkeys.accept("s", self.setKey, ["cam-right",1])
        self.game.gui.hotkeys.accept("arrow_left-up", self.setKey, ["left",0])
        self.game.gui.hotkeys.accept("arrow_right-up", self.setKey, ["right",0])
        self.game.gui.hotkeys.accept("arrow_up-up", self.setKey, ["forward",0])
        self.game.gui.hotkeys.accept("a-up", self.setKey, ["cam-left",0])
        self.game.gui.hotkeys.accept("s-up", self.setKey, ["cam-right",0])
        self.game.gui.hotkeys.accept("f2", self.toggleDebug)

        self.game.char.setPos(self.game.world.chunks_map.charRX,
                              self.game.world.chunks_map.charRY,
                              self.game.world.chunks_map.charZ)

        self.head.setY(self.char.getY())
        self.head.setX(self.char.getX())
        self.head.setZ(self.char.getZ()+2)

        self.cTrav = CollisionTraverser()

        self.charGroundRay = CollisionRay()
        self.charGroundRay.setOrigin(0,0,1000)
        self.charGroundRay.setDirection(0,0,-1)
        self.charGroundCol = CollisionNode('charRay')
        self.charGroundCol.addSolid(self.charGroundRay)
        self.charGroundColNp = self.char.attachNewNode(self.charGroundCol)
        self.charGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.charGroundColNp, self.charGroundHandler)

        if self.enable:
            self.game.char.reparentTo(self.game.gui.render)
        else:
            self.game.char.detachNode()

    def setKey(self, key, value):
        self.keyMap[key] = value

    def toggleDebug(self):
        if self.isDebug:
            # Uncomment this line to see the collision rays
            self.charGroundColNp.hide()
            # Uncomment this line to show a visual representation of the
            # collisions occuring
            self.cTrav.hideCollisions()
        else:
            # Uncomment this line to see the collision rays
            self.charGroundColNp.show()
            # Uncomment this line to show a visual representation of the
            # collisions occuring
            self.cTrav.showCollisions(render)
        self.isDebug = not self.isDebug
        print 'Collision debug: ', self.isDebug

    def move(self, task):

        if not self.enable:
            return task.cont

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.


        # save char's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        #self.char.setZ(self.game.world.chunks_map.land_z)


        startpos = self.char.getPos()

        self.head.setY(self.char.getY())
        self.head.setX(self.char.getX())
        self.head.setZ(self.char.getZ()+2)

        md = self.game.gui.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        oldH = self.head.getH()
        oldP = self.head.getP()

        if self.game.gui.win.movePointer(0, self.game.gui.win.getXSize()/2, self.game.gui.win.getYSize()/2):
            self.head.setH(oldH - (x - self.game.gui.win.getXSize()/2)*self.SpeedRot)
            self.head.setP(oldP - (y - self.game.gui.win.getYSize()/2)*self.SpeedRot)
            if (self.head.getP() <= -90.1):
                self.head.setP(-90)
            if (self.head.getP() >= 90.1):
                self.head.setP(90)

        if (self.keyMap["forward"]!=0):
            self.char.setY(self.char, + 20 * globalClock.getDt())

        self.char.setH(self.head.getH())
        #self.char.setP(self.game.gui.camera.getP())
        # If char is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.char.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.char.stop()
                self.char.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from char, move it closer.
        # If the camera is too close to char, move it farther.

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust char's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        #entries = []
        #for i in range(self.charGroundHandler.getNumEntries()):
            #entry = self.charGroundHandler.getEntry(i)
            #entries.append(entry)
        #entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     #x.getSurfacePoint(render).getZ()))
        #if (len(entries)>0):
            #print 'char collision entries: ', entries
            #self.char.setZ(entries[0].getSurfacePoint(render).getZ())
        #else:
            #self.char.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above char, whichever is greater.

        return task.cont

