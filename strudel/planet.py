from strudel.spheregeo import SphereNode
from direct.task import Task
from pandac.PandaModules import Vec3, Vec3D, Vec4, PNMImage
from pandac.PandaModules import Shader, Texture, TextureStage
from pandac.PandaModules import PointLight, NodePath, PandaNode
from pandac.PandaModules import Point3D
import random, os
import glob
from math import pi, sin, cos

from strudel.view import View
from strudel.model import Model
from strudel.star import Star
from strudel.units import AU, Sol

class Planet(Model):
    @classmethod
    def random(cls):
        return cls()

    def __init__(self, **kwargs):
        super(Planet, self).__init__(**kwargs)

    def recalc_pos(self):
        x = self.apsis * AU * cos(self.theta)
        y = self.apsis * AU * sin(self.theta)
        z = 0
        self.pos = self.orbiting.pos + Point3D(x,y,z)
        return self.pos

    @property
    def star(self):
        if isinstance(self.orbiting, Star):
            return self.orbiting
        else:
            return self.orbiting.star

    @property
    def radius_km(self):
        return self.radius*Sol.radius

class ParamSet(object):
    def __init__( self, seedparam ):
        self.vectors = {}
        self.vectors["seed"    ] = seedparam
        self.vectors["bias12"  ] = Vec4(0,0,0,0)
        self.vectors["bias34"  ] = Vec4(0,0,0,0.0)
        self.vectors["scale"   ] = Vec4(0.3,0.3,0.3,0.3)
        self.vectors["aspect"  ] = Vec4(1,1,0.7,0.7)
        self.vectors["latitude"] = Vec4(0.5,0.0,0.0,0.0)
        self.vectors["noisemix"] = Vec4(0,0,1,1)

class PlanetView(View):
    ready = False

    @classmethod
    def setup(cls, loader):
        cls.noisetex = loader.load3DTexture("texture/noise/fbm_###.tif")
        cls.noisestage = TextureStage('noise')
        cls.layer1stage = TextureStage('layer1')
        cls.layer2stage = TextureStage('layer2')
        cls.layer3stage = TextureStage('layer3')
        cls.layer4stage = TextureStage('layer4')
        cls.texture_sets = {}

        layernames = ["layer1", "layer2", "layer3", "layer4"]
        stages = [cls.layer1stage, cls.layer2stage, cls.layer3stage, cls.layer4stage]
        texture_files = os.listdir("texture/planet/layers/")
        for filename in texture_files:
            name,ext = os.path.splitext(filename)
            if name.endswith( "layer1" ):
                paths = [ "texture/planet/layers/" + filename.replace("layer1",layer) for layer in layernames ]
                if all( os.path.exists( path ) for path in paths ):
                    setname = name.replace("layer1","").strip("_")
                    texture_set = [ (cls.noisestage,cls.noisetex) ]
                    for stage,path in zip(stages,paths):
                        tex = loader.loadTexture( path )
                        tex.setWrapU( Texture.WMClamp )
                        tex.setWrapV( Texture.WMClamp )
                        texture_set.append( (stage, tex) )
                    cls.texture_sets[setname] = texture_set

        cls.ready = True

    def __init__(self, parent, planet, **kwargs):
        super(PlanetView, self).__init__(parent, planet, **kwargs)
        if not PlanetView.ready: PlanetView.setup(self.base.loader)
        self.node = NodePath(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/planet.cg"))
        self.cloudtime = 0.0
        self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        self.compute_seed_param()
        for stage, tex in PlanetView.texture_sets['terrestrial_big']:
            self.node.setTexture(stage, tex)

        self.setup_shader_inputs()
        self.node.setScale(1/self.node.getBounds().getRadius())
        self.node.reparentTo(self.parent.node)

    def set_light(self, light):
        self.node.setShaderInput("light", light)
        self.node.setShaderInput("lightcolor", Vec4(light.getColor()))

    def compute_seed_param(self):
        rng = random.Random()
        rng.seed(self.seed)
        self.param_set.vectors["seed"] = Vec4(rng.random(), rng.random(), rng.random(), self.cloudtime)
        self.setup_shader_inputs()

    def setup_shader_inputs(self):
        for k, v in self.param_set.vectors.iteritems():
            self.node.setShaderInput(k, v)
        self.node.setShaderInput("eye", self.base.camera)

    def tick(self, elapsed):
        self.cloudtime += elapsed * 0.02
        self.compute_seed_param()
        self.setup_shader_inputs()
