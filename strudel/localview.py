from pandac.PandaModules import NodePath, Point3
from strudel.view import View
from strudel.star import StarView
from strudel.planet import PlanetView
from strudel.ship import ShipView

class LocalView(View):
    """The pseudo-2D main display where the locality is likely to spend
       most of their time."""

    def update_ship(self, view):
        ship = view.obj
        pos3 = Point3(ship.pos.x, ship.pos.y, ship.pos.z)
        view.node.setPos(pos3)
        view.node.setHpr(ship.hpr)

    def __init__(self, parent, locality, **kwargs):
        super(LocalView, self).__init__(parent, locality, **kwargs)
        self.node = NodePath('local')

        self.scalefactor = 1

        starview = StarView(self, locality.star)
        starview.node.setScale(100)
        self.starview = starview

        self.planet_views = []
        for planet in locality.planets:
            pview = PlanetView(self, planet)
            pview.set_light(starview.light)
            planet.recalc_pos()
            pos = Point3(planet.pos.x, planet.pos.y, planet.pos.z) * self.scalefactor
            pview.node.setPos(pos)
            self.planet_views.append(pview)

        self.ship_views = {}
        for ship in locality.ships:
            view = ShipView(self, ship)
            ship.on('reposition', lambda: self.update_ship(view))
            self.update_ship(view)
            self.ship_views[ship] = view

        self.node.reparentTo(self.parent.node)
