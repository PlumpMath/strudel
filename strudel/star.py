#!/usr/bin/env python

from strudel.spheregeo import SphereNode
from direct.task import Task
from pandac.PandaModules import Vec3, Vec3D, Vec4, PNMImage
from pandac.PandaModules import Shader, Texture, TextureStage
from pandac.PandaModules import PointLight, NodePath, PandaNode
from pandac.PandaModules import ColorBlendAttrib
import random, os
import glob

from direct.filter.CommonFilters import CommonFilters

from stellar_class import StellarClass

class Star(object):
    @classmethod
    def random(cls):
        return cls(StellarClass.getRandom())

    def __init__(self, sclass):
        if isinstance(sclass, str):
            sclass = StellarClass.get(sclass)
        self.sclass = sclass

    def __getattr__(self, name):
        return getattr(self.sclass, name)

    @property
    def color(self):
        return Vec4(self.red, self.green, self.blue, 1)

class ParamSet(object):
    def __init__( self, seedparam ):
        self.vectors = {}
        self.vectors["seed"    ] = seedparam
        self.vectors["bias12"  ] = Vec4(0,0,0,0)
        self.vectors["bias34"  ] = Vec4(0,0,0,0.0)
        self.vectors["aspect"  ] = Vec4(1,1,0.7,0.7)
        self.vectors["latitude"] = Vec4(0.5,0.0,0.0,0.0)
        self.vectors["scale"] = Vec4(0.3, 0.3, 0.2, 0.4)
        self.vectors["noisemix"] = Vec4(0,0,1,1)

class StarDisplay(object):
    ready = False

    min_scale = Vec4(0.3, 0.3, 0.2, 0.4)
    max_scale = Vec4(0.6, 0.6, 0.4, 0.8)

    @classmethod
    def setup(cls, base):
        cls.noisetex = base.loader.load3DTexture("texture/noise/fbm_###.tif")
        cls.noisestage = TextureStage('noise')
        cls.layer1stage = TextureStage('layer1')
        cls.layer2stage = TextureStage('layer2')
        cls.layer3stage = TextureStage('layer3')
        cls.layer4stage = TextureStage('layer4')

        stages = [cls.layer1stage, cls.layer2stage, cls.layer3stage, cls.layer4stage]
        texture_files = os.listdir("texture/")

        paths = glob.glob("texture/star/layers/*.tif")
        paths.sort()
        cls.texture_set = [ (cls.noisestage,cls.noisetex) ]
        for stage,path in zip(stages,paths):
            tex = base.loader.loadTexture( path )
            tex.setWrapU( Texture.WMClamp )
            tex.setWrapV( Texture.WMClamp )
            cls.texture_set.append( (stage, tex) )

        print cls.texture_set

        cls.ready = True

    def __init__(self, base, star):
        if not StarDisplay.ready: StarDisplay.setup(base)
        self.obj = star

        self.base = base
        self.seed = random.random()

        plight = PointLight("starlight")
        plight.setColor(self.obj.color)
        self.light = base.render.attachNewNode(plight)

        self.node = self.light.attachNewNode(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/starshader.cg"))
        self.cloudtime = 0.0
        self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        self.compute_seed_param()

        for stage, tex in StarDisplay.texture_set:
            self.node.setTexture(stage, tex)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.speed = 0.00000001
        self.lasttime = 0.0
        self.setup_shader_inputs()

        base.displays.append(self)

    def compute_seed_param(self):
        rng = random.Random()
        rng.seed(self.seed)
        self.param_set.vectors["seed"] = Vec4(rng.random(), rng.random(), rng.random(), self.cloudtime)
        self.setup_shader_inputs()

    def setup_shader_inputs(self):
        for k, v in self.param_set.vectors.iteritems():
            self.node.setShaderInput(k, v)
        self.node.setShaderInput("starcolor", Vec4(1,0,0,1))#self.obj.color)
        self.node.setShaderInput("eye", self.base.camera)

    def tick(self, time):
        elapsed = time - self.lasttime
        self.lasttime = time
        self.cloudtime += elapsed * 0.02
        self.yaw += 360.0 * self.speed * elapsed
        self.node.setHpr(self.yaw, self.pitch, self.roll)
        self.compute_seed_param()
        self.setup_shader_inputs()

    def remove(self):
        self.node.remove()
        self.base.displays.remove(self)
