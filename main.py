#!/usr/bin/env python

class Star(object):
    pass

from strudel.spheregeo import SphereNode
from direct.task import Task
from pandac.PandaModules import Vec3, Vec3D, Vec4, PNMImage
from pandac.PandaModules import Shader, Texture, TextureStage
from pandac.PandaModules import PointLight, NodePath, PandaNode
from pandac.PandaModules import ColorBlendAttrib
import random, os

from direct.filter.CommonFilters import CommonFilters

param_sets = {}


class Planet(object):
    pass

class ParamSet( object ):
    def __init__( self, seedparam ):
        self.vectors = {}
        self.vectors["seed"    ] = seedparam
        self.vectors["bias12"  ] = Vec4(0,0,0,0)
        self.vectors["bias34"  ] = Vec4(0,0,0,0.0)
        self.vectors["scale"   ] = Vec4(0.4,0.4,0.3,0.6)
        self.vectors["aspect"  ] = Vec4(1,1,0.7,0.7)
        self.vectors["latitude"] = Vec4(0.5,0.0,0.0,0.0)
        self.vectors["noisemix"] = Vec4(0,0,1,1)

class PlanetDisplay(object):
    ready = False

    @classmethod
    def setup(cls, app):
        cls.noisetex = app.loader.load3DTexture("texture/fbm_###.tif")
        cls.noisestage = TextureStage('noise')
        cls.layer1stage = TextureStage('layer1')
        cls.layer2stage = TextureStage('layer2')
        cls.layer3stage = TextureStage('layer3')
        cls.layer4stage = TextureStage('layer4')
        cls.texture_sets = {}

        layernames = ["layer1", "layer2", "layer3", "layer4"]
        stages = [cls.layer1stage, cls.layer2stage, cls.layer3stage, cls.layer4stage]
        texture_files = os.listdir("texture/")
        for filename in texture_files:
            name,ext = os.path.splitext(filename)
            if name.endswith( "layer1" ):
                paths = [ "texture/" + filename.replace("layer1",layer) for layer in layernames ]
                #print paths
                if all( os.path.exists( path ) for path in paths ):
                    setname = name.replace("layer1","").strip("_")
                    #print "Found layer set - %s"%setname
                    texture_set = [ (cls.noisestage,cls.noisetex) ]
                    for stage,path in zip(stages,paths):
                        tex = app.loader.loadTexture( path )
                        tex.setWrapU( Texture.WMClamp )
                        tex.setWrapV( Texture.WMClamp )
                        texture_set.append( (stage, tex) )
                    cls.texture_sets[setname] = texture_set

        cls.ready = True


    def __init__(self, app, planet):
        if not PlanetDisplay.ready: PlanetDisplay.setup(app)
        self.node = app.render.attachNewNode(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/starshader.cg"))
        self.cloudtime = 0.0
        self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        self.compute_seed_param()

        for stage, tex in PlanetDisplay.texture_sets['sun_big']:
            self.node.setTexture(stage, tex)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.speed = 0.00000001
        self.lasttime = 0.0
        self.setup_shader_inputs()

    def compute_seed_param(self):
        rng = random.Random()
        rng.seed(self.seed)
        self.param_set.vectors["seed"] = Vec4(rng.random(), rng.random(), rng.random(), self.cloudtime)
        self.setup_shader_inputs()

    def setup_shader_inputs(self):
        for k, v in self.param_set.vectors.iteritems():
            self.node.setShaderInput(k, v)

    def tick(self, time):
        elapsed = time - self.lasttime
        self.lasttime = time
        self.cloudtime += elapsed * 0.02
        self.yaw += 360.0 * self.speed * elapsed
        self.node.setHpr(self.yaw, self.pitch, self.roll)
        self.compute_seed_param()
        self.setup_shader_inputs()


class Ship(object):
    pass

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile

loadPrcFile("init/panda.prc")

class StrudelApp(ShowBase):
    def makeFilterBuffer(self, srcbuffer, name, sort, prog):
      blur_buffer = self.win.makeTextureBuffer(name, 512, 512)
      blur_buffer.setSort(sort)
      blur_buffer.setClearColor(Vec4(1,0,0,1))
      blur_camera = self.makeCamera2d(blur_buffer)
      blur_scene = NodePath("new Scene")
      blur_camera.node().setScene(blur_scene)
      shader = self.loader.loadShader(prog)
      card = srcbuffer.getTextureCard()
      card.reparentTo(blur_scene)
      card.setShader(shader)
      return blur_buffer


    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0, 0, 0)
        self.disableMouse()

        self.accept("enter", self.show_planet)

        self.filters = CommonFilters(self.win, self.cam)

        self.planet = Planet()
        self.show_planet()

    def show_planet(self):

        if hasattr(self.planet, 'display'):
            self.planet.display.node.removeNode()

#        self.lightpivot = self.render.attachNewNode("lightpivot")
#        self.lightpivot.setPos(0,0,0)
#        plight = PointLight('plight')
#        plight.setColor(Vec4(1, 1, 1, 1))
#        plight.setAttenuation(Vec3(0.7,0.05,0))
#        plnp = self.lightpivot.attachNewNode(plight)
#        plnp.setPos(0, 0, -10)

        sunlight = PointLight('sunlight')
        sunlight.setColor(Vec4(1, 0.9, 0.9, 1))
        slnode = self.render.attachNewNode(sunlight)

        self.planet.display = PlanetDisplay(self, self.planet)
        self.planet.display.seed = random.random()
        plnode = self.planet.display.node
        plnode.setShaderInput("light", slnode)
        plnode.setShaderInput("eye", self.camera)
        plnode.setShaderInput("lightcolor", Vec4(1.0, 1.0, 1.0, 1.0))

        plnode.reparentTo(slnode)

        self.render.setShaderAuto()
        self.filters.setBloom(blend=(0.5,0.5,0.5,1), desat=-2.0, intensity=9.0, size="medium")

#        glow_shader=self.loader.loadShader("shader/glowShader.cg")
#        glow_buffer=self.win.makeTextureBuffer("Glow scene", 512, 512)
#        glow_buffer.setSort(-3)
#        glow_buffer.setClearColor(Vec4(0,0,0,1))
#        self.glowcam=self.makeCamera(glow_buffer, lens=self.cam.node().getLens())
#        tempnode = NodePath(PandaNode("temp node"))
#        tempnode.setShader(glow_shader)
#        self.glowcam.node().setInitialState(tempnode.getState())
#        self.glowcam.reparentTo(self.cam)
#        blurXBuffer=self.makeFilterBuffer(glow_buffer,  "Blur X", -2, "shader/XBlurShader.cg")
#        blurYBuffer=self.makeFilterBuffer(blurXBuffer, "Blur Y", -1, "shader/YBlurShader.cg")
#        self.finalcard = blurYBuffer.getTextureCard()
#        self.finalcard.reparentTo(self.render2d)
#        self.finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
#
#        self.accept("v", self.bufferViewer.toggleEnable)
#        self.accept("V", self.bufferViewer.toggleEnable)
#        self.bufferViewer.setPosition("llcorner")
#        self.bufferViewer.setLayout("hline")
#        self.bufferViewer.setCardSize(0.652,0)
#
        self.camera.setPos(0, 0, -4)
        self.camera.lookAt(plnode)


        def update_planet_task(task):
            self.planet.display.tick(task.time)
            return Task.cont

        self.taskMgr.add(update_planet_task, "updateself.planet")

if __name__ == '__main__':
    app = StrudelApp()
    app.run()
