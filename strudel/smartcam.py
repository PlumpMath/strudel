from pandac.PandaModules import Camera, NodePath

class SmartCam(object):
    def __init__(self, nameorcam):
        if isinstance(nameorcam, NodePath):
            self.node = nameorcam
        else:
            self.node = Camera(nameorcam)

    def __getattr__(self, name):
        return getattr(self.node, name)

    @property
    def fpos(self):
        return self.focus.getPos()

    def sync_focus(self):
        self.node.setPos(self.fpos.x, self.fpos.y, self.fpos.z-self.zoom_height)
        self.node.lookAt(self.fpos)

    def set_focus(self, focus):
        self.focus = focus
        self.zoom_height = self.focal_radius/2
        self.sync_focus()

    @property
    def focal_radius(self):
        return self.focus.getBounds().getRadius()

    def zoom_in(self):
        self.zoom_height = max(0.5, self.zoom_height*0.9 - self.focal_radius/10)
        self.sync_focus()
        #self.node.setZ(-(self.focal_radius/2+new_height))

    def zoom_out(self):
        self.zoom_height = max(0.5, self.zoom_height*1.1 + self.focal_radius/10)
        self.sync_focus()
