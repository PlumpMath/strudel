#!/usr/bin/env python

import logging
logging.basicConfig(format='[%(module)s] %(message)s', level=logging.DEBUG)

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

        # HACK (Mispy): This disables the alt-modifier in order to
        # workaround a compatibility issue with Panda on some Linux
        # systems where alt+tab never sends an alt-up event, causing
        # the loss of subsequent input until alt is pressed again.
        buttons = base.mouseWatcherNode.getModifierButtons()
        buttons.removeButton(buttons.getButton(2))
        base.mouseWatcherNode.setModifierButtons(buttons)
        base.buttonThrowers[0].node().setModifierButtons(buttons)

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

    def on_window_event(self, win):
        if win.isClosed():
            sys.exit()
        else:
            width = win.getProperties().getXSize()
            height = win.getProperties().getYSize()
            self.cam.node().getLens().setFilmSize(width, height)
            #self.cam.node().getLens().setFocalLength(FOCAL_LENGTH)

    def setup(self):
        self.lasttime = 0.0
        self.pressed = {}
        self.accept("escape", sys.exit)
        self.accept("`", self.debug_shell)
        self.accept("f12", self.reload_app)
        self.accept(self.win.getWindowEvent(), self.on_window_event)
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
        self.setup()

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
            # XXX (Mispy): The IPython mainloop runs quite slowly
            # and causes massive FPS loss. I don't know how to solve
            # this but I believe it is solvable.
            inputhook.set_inputhook(self.step)
            embed()
        return 0

    def load_galaxy(self, name):
        self.galaxy = Galaxy.load(name)

if __name__ == '__main__':
    base = StrudelApp()
    if len(sys.argv) > 1 and sys.argv[1] == "new_galaxy":
        galaxy = GalaxyGenerator.barred_spiral('testing')
        galaxy.save()
        sys.exit()

    base.load_galaxy('testing')
    if len(sys.argv) > 1:
        if sys.argv[1] == "inspect":
            base.inspector.inspect(eval(sys.argv[2]))

    base.setup()
    while True:
        base.step()

