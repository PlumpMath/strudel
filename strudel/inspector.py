from strudel.star import Star, StarView
from strudel.planet import Planet, PlanetView
from strudel.star_system import StarSystem
from strudel.sysview import StarSystemView
from strudel.galaxy import GalaxyGenerator
from strudel.galaxy_view import GalaxyView
from strudel.ship import Ship, ShipView
from pandac.PandaModules import Vec4, PointLight
import random
from math import tan, pi

class ObjectInspector(object):
    """Provides functions to graphically inspect an object in isolation."""

    def __init__(self, base):
        self.base = base

    def slowly_rotate(self, view, speed=0.01):
        def tick(elapsed):
            if not self.base.pressed['mouse3']:
                view.node.setH(view.node.getH() + 360.0 * elapsed * speed)
        view.on('tick', tick)

    def fov_wrap(self, node, factor=1):
        radius = node.getBounds().getRadius()
        encompassing_zoom = radius*factor / (2.0 * tan(self.base.camLens.getFov().y * pi/180.0 * 0.5))
        self.base.camera.setPos(0, 0, -encompassing_zoom)
        self.base.camera.lookAt(node)

    def inspect_galaxy(self, galaxy):
        view = GalaxyView(self.base, galaxy)
        self.fov_wrap(view.node)
        self.slowly_rotate(view)
        self.base.accept("enter", lambda: self.inspect(GalaxyGenerator.barred_spiral('tmp')))
        self.view = view

    def inspect_star(self, star):
        view = StarView(self.base, star)
        self.base.render.setShaderAuto()
        self.base.filters.setBloom(blend=(0.5,0.5,0.5,0), desat=-2.0, intensity=8.0, size="medium")
        self.base.filters.setBlurSharpen(amount=0.8)
        self.fov_wrap(view.node)
        self.base.accept("enter", lambda: self.inspect(random.choice(star.galaxy.stars)))
        self.slowly_rotate(view)
        self.view = view

    def inspect_planet(self, planet):
        plight = PointLight('plight')
        plight.setColor(Vec4(1,1,1,1))
        plnp = self.base.render.attachNewNode(plight)
        plnp.setPos(-50,-100,50)
        view = PlanetView(self.base, planet)
        view.set_light(plnp)
        self.base.camera.setPos(0, 0, -4)
        self.base.camera.lookAt(view.node)
        self.base.accept("enter", lambda: self.inspect(random.choice(planet.galaxy.planets)))
        self.slowly_rotate(view)
        self.view = view

    def inspect_starsystem(self, system):
        view = StarSystemView(self.base, system)
        self.fov_wrap(view.node, 2)
        #self.slowly_rotate(view)
        self.base.accept("enter", lambda: self.inspect(StarSystem(random.choice(system.galaxy.stars))))
        self.view = view

    def inspect_ship(self, ship):
        view = ShipView(self.base, ship)
        self.fov_wrap(view.node)
        self.slowly_rotate(view)
        self.view = view

    def inspect(self, obj):
        self.obj = obj
        classname = obj.__class__.__name__
        funcname = "inspect_" + classname.lower()
        if not hasattr(self, funcname):
            raise NotImplementedError, "I don't know how to inspect a %s, sorry!" % classname

        self.base.cleanup()
        self.base.setup()

        getattr(self, funcname)(obj)

        def drag_rotate(xdiff, ydiff):
            hpr = self.view.node.getHpr()
            self.view.node.setHpr(hpr.x, hpr.y - ydiff*100, hpr.z - xdiff*100)
        #self.base.on('drag', drag_rotate)

        focal_radius = self.view.node.getBounds().getRadius()

        def zoom_in():
            campos = self.base.camera.getPos()
            zoom_height = abs(campos.z)-focal_radius/2
            new_height = max(0.5, zoom_height*0.9 - focal_radius/10)
            self.base.camera.setZ(-(focal_radius/2+new_height))

        def zoom_out():
            campos = self.base.camera.getPos()
            zoom_height = abs(campos.z)-focal_radius/2
            new_height = max(0.5, zoom_height*1.1 + focal_radius/10)
            self.base.camera.setZ(-(focal_radius/2+new_height))

        self.base.accept("wheel_up", zoom_in)
        self.base.accept("wheel_down", zoom_out)

        self.base.show_text(repr(obj))


