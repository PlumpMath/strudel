#!/usr/bin/env python

from strudel.stellar_class import StellarClass
from strudel.galaxy import Galaxy, GalaxyGenerator
from strudel.star import Star, StarView
from strudel.planet import Planet, PlanetView


from strudel.spheregeo import SphereNode
from direct.task import Task
from pandac.PandaModules import Vec3, Vec3D, Vec4, PNMImage
from pandac.PandaModules import Shader, Texture, TextureStage
from pandac.PandaModules import PointLight, NodePath, PandaNode
from pandac.PandaModules import ColorBlendAttrib
import random, os
import sys

from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode

loadPrcFile("init/panda.prc")

from strudel.evented import Evented
from strudel.inspector import ObjectInspector

class StrudelApp(ShowBase, Evented):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0)
        self.disableMouse()

        self.filters = CommonFilters(self.win, self.cam)
        self.views = []
        self.texts = []
        self.want_shell = False
        self.inspector = ObjectInspector(self)

    def drag_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            if self.pressed['mouse3']:
                self.emit('drag', self.rotateStartX-mpos.getX(), self.rotateStartY-mpos.getY())
            self.rotateStartX = self.mouseWatcherNode.getMouseX()
            self.rotateStartY = self.mouseWatcherNode.getMouseY()
        return Task.cont

    def tick_task(self, task):
        elapsed = task.time - self.lasttime
        self.emit('tick', elapsed)
        for view in self.views:
            if hasattr(view, 'tick'):
                view.emit('tick', elapsed)
        self.lasttime = task.time
        return Task.cont

    def debug_shell(self):
        self.want_shell = True

    def reload_app(self):
        print "raffle"
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def base_setup(self):
        self.lasttime = 0.0
        self.pressed = {}
        self.accept("escape", sys.exit)
        self.accept("`", self.debug_shell)
        self.accept("f12", self.reload_app)
        for button in ["mouse1", "mouse2", "mouse3"]:
            self.pressed[button] = False
            def button_down(button=button): self.pressed[button] = True
            def button_up(button=button): self.pressed[button] = False
            self.accept(button, button_down)
            self.accept(button+"-up", button_up)

        self.taskMgr.add(self.tick_task, "tick_task")
        self.taskMgr.add(self.drag_task, "drag_task")

    def cleanup_text(self):
        for text in self.texts:
            text.destroy()
        self.texts = []

    def cleanup(self):
        """Reset application to a clean slate so we can move to another state."""
        for view in self.views:
            view.remove()

        for child in self.render.getChildren():
            if child != self.camera:
                child.removeNode()

        self.cleanup_text()

        self.messenger.clear()
        self.taskMgr.removeTasksMatching('task')
        self.clear_handlers()
        self.base_setup()

    def show_text(self, lines):
        if isinstance(lines, str): lines = [lines]
        self.cleanup_text()
        ypos = 0.9
        for line in lines:
            text = OnscreenText(text=line, pos=(-1.3,ypos), style=1, fg=(1,1,1,1),
                                align=TextNode.ALeft, scale=0.05, parent=self.aspect2d)
            text.reparentTo(self.aspect2d)
            self.texts.append(text)
            ypos -= 0.05

    def step(self):
        self.taskMgr.step()
        if self.want_shell:
            self.want_shell = False
            from IPython import embed
            from IPython.lib import inputhook
            inputhook.set_inputhook(self.step)
            embed()
        return 0

if __name__ == '__main__':
    base = StrudelApp()
    if len(sys.argv) > 1:
        if sys.argv[1] == "view_object":
            base.inspector.inspect(eval(sys.argv[2]))

    # Run IPython alongside Strudel; unfortunately quite slow
    # from IPython import embed
    # from IPython.lib import inputhook
    # inputhook.set_inputhook(base.step)
    # embed()

    while True:
        base.step()

