from panda3d.core import Vec3
from panda3d.core import VBase3

import uuid

v = [Vec3(0,0,-1), Vec3(0,0,1), Vec3(0,-1,0), Vec3(0,1,0), Vec3(-1,0,0), Vec3(1,0,0)]
max_len = 256
r = max_len*2**0.5 


class App:
    app = None
    #def link(self, app_link = None):
    #    self.app = app_link
    #    return app
    
app = App() 

class OctreeNode:
    stop = False        
    child = []
    #cube
    def __init__(self, myapp, len, parent=None, level = 1, center = Vec3(0,0,0)):
        self.parent = parent
        self.level = level
        self.center = center
        self.len = len
        self.myapp = myapp
        self.cube = myapp.loader.loadModel("models/box")
        if self.check():
            self.draw()      

    def divide(self):
        if not self.stop:
            for dC in v:         
                self.child.append(__OctreeNode(self, self.len/2, self.level+1, self.center+dC*length/2))

    def check(self):
        #if dist higher then sphere radius then stop dividind
        if VBase3.length(self.center) > r: self.stop = True 
        #stop at bottom level
        if self.len == 1: self.stop = True
        return not self.stop

    def draw(self):                    
        if self.level == 1:            
            #TODO: SHOW CUBE HERE            
            self.cube.setScale(self.len/2, self.len/2, self.len/2)
            self.cube.setPos(self.center)
            self.cube.reparentTo(render)

class VoxObject:   
    def __init__(self, app_link):
        self.app = app_link
        #self.app.environ = app_link.loader.loadModel("models/box")
        self.root = OctreeNode(self.app, max_len)
         

        
         
   
            
        
