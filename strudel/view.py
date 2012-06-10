from direct.showbase.ShowBase import ShowBase
from strudel.evented import Evented

class View(Evented):
    """Abstract class for object renderers!

     If you consider Panda3D and the graphical interface as the
     "controller" part of MVC architecture, then this is the "view"
     """
    def __init__(self, parent, obj):
        self.children = [] # Views dependent on this one.
        self.obj = obj
        self.parent = parent
        self.parent.children.append(self)
        self.on('tick', lambda time: self.tick(time))

    def cleanup(self):
        self.event_cleanup()
        for view in list(self.children): view.remove()
        assert(len(self.children) == 0)

    def remove(self):
        self.cleanup()
        if hasattr(self, 'node'): self.node.remove()
        self.parent.children.remove(self)

    def hide(self):
        self.node.hide()

    def show(self):
        self.node.show()

    def tick(self, time):
        for view in self.children:
            view.tick(time)

    @property
    def base(self):
        if isinstance(self.parent, ShowBase):
            return self.parent
        else:
            return self.parent.base

