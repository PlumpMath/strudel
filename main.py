#!/usr/bin/env python

from strudel.stellar_class import StellarClass
from strudel.star import Star, StarDisplay


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

loadPrcFile("init/panda.prc")

from strudel.evented import Evented

class StrudelApp(ShowBase, Evented):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0)
        self.disableMouse()

        self.filters = CommonFilters(self.win, self.cam)
        self.displays = []

    def drag_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            if self.pressed['mouse3']:
                self.emit('drag', self.rotateStartX-mpos.getX(), self.rotateStartY-mpos.getY())
            self.rotateStartX = self.mouseWatcherNode.getMouseX()
            self.rotateStartY = self.mouseWatcherNode.getMouseY()
        return Task.cont

    def update_task(self, task):
        for display in self.displays:
            display.tick(task.time)
        return Task.cont

    def base_setup(self):
        self.pressed = {}
        for button in ["mouse1", "mouse2", "mouse3"]:
            self.pressed[button] = False
            def button_down(): self.pressed[button] = True
            def button_up(): self.pressed[button] = False
            self.accept(button, button_down)
            self.accept(button+"-up", button_up)

        self.taskMgr.add(self.update_task, "update_task")
        self.taskMgr.add(self.drag_task, "drag_task")

    def cleanup(self):
        for display in self.displays:
            display.remove()
        for child in self.render.getChildren():
            if child != self.camera:
                child.removeNode()
        self.messenger.clear()
        self.taskMgr.removeTasksMatching('task')
        self.clear_handlers()
        self.base_setup()

    def view_object(self, obj):
        self.cleanup()
        def drag_rotate(xdiff, ydiff):
            obj.display.roll = obj.display.roll - xdiff*100
            obj.display.pitch = obj.display.pitch - ydiff*100
        self.on('drag', drag_rotate)
        if isinstance(obj, Star):
            print obj.sclass
            obj.display = StarDisplay(self, obj)
            self.render.setShaderAuto()
            self.filters.setBloom(blend=(0.5,0.5,0.5,0), desat=-2.0, intensity=8.0, size="medium")
            self.filters.setBlurSharpen(amount=0.5)
            self.camera.setPos(0, 0, -4)
            self.camera.lookAt(obj.display.node)
            self.accept("enter", lambda: self.view_object(Star.random()))

if __name__ == '__main__':
    app = StrudelApp()
    if len(sys.argv) > 1:
        if sys.argv[1] == "view_object":
            app.view_object(eval(sys.argv[2]))
    app.run()

