from pandac.PandaModules import NodePath, Point3
from strudel.view import View
from strudel.star import Star, StarView
from strudel.planet import Planet, PlanetView
from strudel.ship import Ship, ShipView
from strudel.util import propdict

class LocalView(View):
    """The pseudo-2D main display where the player is likely to spend
       most of their time."""

    def update_ship(self, view):
        ship = view.obj
        pos3 = Point3(ship.pos.x, ship.pos.y, ship.pos.z)
        view.node.setPos(pos3)
        view.node.setHpr(ship.hpr)

    def view_for(self, obj):
        if isinstance(obj, Star):
            if not self.views.has_key('star'):
                self.views.star = StarView(self, obj)
            return self.views.star
        elif isinstance(obj, Planet):
            if not self.views.planets.has_key(obj):
                self.views.planets[obj] = PlanetView(self, obj)
            return self.views.planets[obj]
        elif isinstance(obj, Ship):
            try: return self.views.ships[obj]
            except KeyError:
                shipview = ShipView(self, obj)
                self.delegate(obj, 'reposition', lambda: self.update_ship(shipview))
                self.views.ships[obj] = shipview
                return shipview
        else:
            raise NotImplementedError

    def render(self):
        starview = self.view_for(self.locality.star)
        starview.node.setScale(100)

        for planet in self.locality.planets:
            pview = self.view_for(planet)
            pview.set_light(starview.light)
            planet.recalc_pos()
            pos = Point3(planet.pos.x, planet.pos.y, planet.pos.z) * self.distance_scale
            pview.node.setPos(pos)
            pview.node.setScale(100)

        for ship in self.locality.ships:
            view = self.view_for(ship)
            self.update_ship(view)

    def __init__(self, parent, locality, **kwargs):
        super(LocalView, self).__init__(parent, locality, **kwargs)
        self.locality = locality
        self.distance_scale = 0.01

        self.views = propdict()
        self.views.planets = {}
        self.views.ships = {}
        self.node = NodePath('local')
        self.node.reparentTo(self.parent.node)

        self.render()
