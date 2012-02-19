from strudel.evented import Evented

class View(Evented):
    """Abstract class for object renderers!

     If you consider Panda3D and the graphical interface as the
     "controller" part of MVC architecture, then this is the "view"
     """
    def __init__(self, base, obj):
        self.obj = obj
        self.base = base
        self.base.views.append(self)
        self.on('tick', lambda time: self.tick(time))

    def remove(self):
        if hasattr(self, 'node'): self.node.remove()
        self.base.views.remove(self)

    def tick(self, time):
        pass
