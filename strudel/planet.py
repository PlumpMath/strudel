from strudel.spheregeo import SphereNode
from direct.task import Task
from pandac.PandaModules import Vec3, Vec3D, Vec4, PNMImage
from pandac.PandaModules import Shader, Texture, TextureStage
from pandac.PandaModules import PointLight, NodePath, PandaNode
from pandac.PandaModules import ColorBlendAttrib
import random, os
import glob

from strudel.view import View

class Planet(object):
    @classmethod
    def random(cls):
        return cls()

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
    def setup(cls, app):
        cls.noisetex = app.loader.load3DTexture("texture/noise/fbm_###.tif")
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

    def __init__(self, base, planet, **kwargs):
        super(PlanetView, self).__init__(base, planet, **kwargs)
        if not PlanetView.ready: PlanetView.setup(base)
        self.node = base.render.attachNewNode(SphereNode(subdivides=4))
        self.node.setShader(Shader.load("shader/planet.cg"))
        self.cloudtime = 0.0
        self.seed = hash("fish")
        self.param_set = ParamSet(self.seed)

        self.compute_seed_param()
        for stage, tex in PlanetView.texture_sets['terrestrial_big']:
            self.node.setTexture(stage, tex)

        self.setup_shader_inputs()

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
