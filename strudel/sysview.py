from math import log
from pandac.PandaModules import NodePath, Point3
from strudel.view import View
from strudel.star import StarView
from strudel.planet import PlanetView
from strudel.ship import ShipIconView


class StarSystemView(View):
    def __init__(self, parent, system, **kwargs):
        super(StarSystemView, self).__init__(parent, system, **kwargs)
        self.refscale = 100
        self.node = NodePath('system')
        planets, stars = [self.obj.planets, self.obj.stars]

        starview = StarView(self, system.star)
        starview.node.setScale(self.refscale)
        self.starview = starview

        # Calculate the smallest distance between any two objects so
        # we can ensure no overlaps even in the worst-case scenarios.
        last_apsis = 0
        min_dist = float("inf")
        for planet in self.obj.planets:
            dist = planet.apsis - last_apsis
            if dist < min_dist: min_dist = dist
            last_apsis = planet.apsis

        scalefactor = system.star.radius/system.star.radius_km
        scalefactor *= (min_dist*1.2)/last_apsis
        scalefactor *= self.refscale/2
        self.scalefactor = scalefactor

        min_radius = min([obj.radius for obj in planets+stars])
        max_radius = max([obj.radius for obj in planets+stars])

        self.planet_views = []
        for planet in planets:
            pview = PlanetView(self, planet)
            pview.set_light(starview.light)
            pview.node.setScale(self.refscale * log(planet.radius_km) / log(system.star.radius_km))
            self.planet_views.append(pview)

        self.update_orbits()

        self.ship_views = {}
        for ship in self.obj.ships:
            self.add_ship(ship)

        #cm = CardMaker('card')
        #radius = last_apsis*AU*scalefactor
        #cm.setFrame(-radius, radius, -radius, radius)
        #trail = self.node.attachNewNode(cm.generate())
        #trail.setP(90)
        #trail.setTwoSided(True)

        self.node.reparentTo(self.parent.node)

    def add_ship(self, ship):
        view = ShipIconView(self, ship)
        #view.node.setLight(self.starview.light)
        view.node.setScale(self.refscale)
        ship.on('reposition', lambda: self.update_ship(view))
        ship.on('reorient', lambda: self.update_ship(view))
        self.update_ship(view)
        self.ship_views[ship] = view

    def update_ship(self, view):
        star = self.obj.star
        rad = self.starview.node.getBounds().getRadius()
        pos3 = Point3(view.obj.pos.x*self.scalefactor, view.obj.pos.y*self.scalefactor, -rad*1.1)
        view.node.setPos(pos3)
        view.node.setHpr(view.obj.hpr)

    def update_orbits(self):
        for pview in self.planet_views:
            planet = pview.obj
            planet.recalc_pos()
            pos3 = Point3(planet.pos.x, planet.pos.y, planet.pos.z) * self.scalefactor
            pview.node.setPos(pos3)

    def tick(self, elapsed):
        self.update_orbits()
        for view in self.children:
            view.tick(elapsed)

