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
from math import log
from strudel.model import Model
from strudel.view import View

class Star(Model):
    @classmethod
    def random(cls):
        return cls(StellarClass.getRandom())

    def __init__(self, sclass, **kwargs):
        super(Star, self).__init__(**kwargs)
        if isinstance(sclass, str):
            sclass = StellarClass.get(sclass)
        self.sclass = sclass

    def __getattr__(self, name):
        if self.__dict__.has_key('sclass'):
            return getattr(self.sclass, name)
        else:
            raise AttributeError

    @property
    def color(self):
        return Vec4(self.red, self.green, self.blue, 1)

    def __repr__(self):
        return "<Star %s [%s]>" % (self.name, self.sclass.name)

class ParamSet(object):
    def __init__( self, seedparam ):
        self.vectors = {}
        self.vectors["seed"    ] = seedparam
        self.vectors["bias12"  ] = Vec4(0,0,0,0)
        self.vectors["bias34"  ] = Vec4(0,0,0,0.0)
        self.vectors["aspect"  ] = Vec4(1,1,0.7,0.7)
        self.vectors["latitude"] = Vec4(0.5,0.0,0.0,0.0)
        self.vectors["noisemix"] = Vec4(0,0,0.5,0.5)

class StarView(View):
    ready = False

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

        cls.ready = True

    def __init__(self, base, star, **kwargs):
        super(StarView, self).__init__(base, star, **kwargs)
        if not StarView.ready: StarView.setup(base)
        self.seed = random.random()

        plight = PointLight("starlight")
        plight.setColor(self.obj.color)
        self.light = base.render.attachNewNode(plight)

        self.node = self.light.attachNewNode(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/star.cg"))
        self.cloudtime = 0.0
        #self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        min_scale = Vec4(0.5, 0.5, 0.5, 0.5)
        max_scale = Vec4(1, 1, 1, 1)
        max_radius = StellarClass.highest_radius
        min_radius = StellarClass.lowest_radius
        radius_factor = log(self.obj.radius*(1/min_radius), 100) / log(max_radius*(1/min_radius), 100)
        self.param_set.vectors['scale'] = min_scale + (max_scale-min_scale)*radius_factor

        self.compute_seed_param()

        for stage, tex in StarView.texture_set:
            self.node.setTexture(stage, tex)

        self.speed = 0.00000001
        self.setup_shader_inputs()

    def compute_seed_param(self):
        rng = random.Random()
        rng.seed(self.seed)
        self.param_set.vectors["seed"] = Vec4(rng.random(), rng.random(), rng.random(), self.cloudtime)
        self.setup_shader_inputs()

    def setup_shader_inputs(self):
        for k, v in self.param_set.vectors.iteritems():
            self.node.setShaderInput(k, v)
        self.node.setShaderInput("starcolor", self.obj.color)
        self.node.setShaderInput("eye", self.base.camera)

    def tick(self, elapsed):
        self.cloudtime += elapsed * 0.05
        self.compute_seed_param()
        self.setup_shader_inputs()
