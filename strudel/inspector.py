from strudel.star import Star, StarView
from strudel.planet import Planet, PlanetView
from strudel.galaxy import GalaxyGenerator
from strudel.galaxy_view import GalaxyView
from pandac.PandaModules import Vec4, PointLight

class ObjectInspector(object):
    """Provides functions to graphically inspect an object in isolation."""

    def __init__(self, base):
        self.base = base

    def slowly_rotate(self, view, speed=0.01):
        def tick(elapsed):
            if not self.base.pressed['mouse3']:
                view.node.setH(view.node.getH() + 360.0 * elapsed * speed)
        view.on('tick', tick)

    def inspect_galaxy(self, galaxy):
        view = GalaxyView(self.base, galaxy)
        self.base.camera.setPos(0, 0, -5000)
        self.base.camera.lookAt(view.node)
        self.slowly_rotate(view)
        self.base.accept("enter", lambda: self.inspect(GalaxyGenerator.barred_spiral('testing')))
        self.view = view

    def inspect_star(self, star):
        view = StarView(self.base, star)
        self.base.render.setShaderAuto()
        self.base.filters.setBloom(blend=(0.5,0.5,0.5,0), desat=-2.0, intensity=8.0, size="medium")
        self.base.filters.setBlurSharpen(amount=0.5)
        self.base.camera.setPos(0, 0, -4)
        self.base.camera.lookAt(view.node)
        self.base.accept("enter", lambda: self.inspect(Star.random()))
        self.slowly_rotate(view)
        self.view = view

    def inspect_planet(self, planet):
        plight = PointLight('plight')
        plight.setColor(Vec4(1,1,1,1))
        plnp = self.base.render.attachNewNode(plight)
        plnp.setPos(-50,-100,50)
        view = PlanetView(self.base, planet)
        view.node.setShaderInput("light", plnp)
        view.node.setShaderInput("lightcolor", Vec4(1.0,1.0,1.0,1.0))
        self.base.camera.setPos(0, 0, -4)
        self.base.camera.lookAt(view.node)
        self.base.accept("enter", lambda: self.inspect(Planet.random()))
        self.slowly_rotate(view)
        self.view = view

    def inspect(self, obj):
        self.obj = obj
        classname = obj.__class__.__name__
        funcname = "inspect_" + classname.lower()
        if not hasattr(self, funcname):
            raise NotImplementedError, "I don't know how to inspect a %s, sorry!" % classname

        self.base.cleanup()

        getattr(self, funcname)(obj)

        def drag_rotate(xdiff, ydiff):
            hpr = self.view.node.getHpr()
            self.view.node.setHpr(hpr.x, hpr.y - ydiff*100, hpr.z - xdiff*100)
        self.base.on('drag', drag_rotate)

        focal_radius = self.view.node.getBounds().getRadius()

        def zoom_in():
            campos = self.base.camera.getPos()
            zoom_height = abs(campos.z)-focal_radius
            new_height = max(0.5, zoom_height*0.9)
            self.base.camera.setZ(-(focal_radius+new_height))

        def zoom_out():
            campos = self.base.camera.getPos()
            zoom_height = abs(campos.z)-focal_radius
            new_height = max(0.5, zoom_height*1.1)
            self.base.camera.setZ(-(focal_radius+new_height))

        self.base.accept("wheel_up", zoom_in)
        self.base.accept("wheel_down", zoom_out)

        self.base.show_text(repr(obj))


