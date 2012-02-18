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

class StrudelApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0)
        self.disableMouse()

        self.filters = CommonFilters(self.win, self.cam)
        self.displays = []

        def update_task(task):
            for display in self.displays:
                display.tick(task.time)
            return Task.cont

        self.taskMgr.add(update_task, "update_task")

    def cleanup(self):
        for display in self.displays:
            display.remove()

    def view_object(self, obj):
        self.cleanup()
        if isinstance(obj, Star):
            print obj.sclass
            obj.display = StarDisplay(self, obj)
            self.render.setShaderAuto()
            self.filters.setBloom(blend=(0.5,0.5,0.5,0), desat=-2.0, intensity=4.0, size="medium")
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

