import random, math
from math import pi
from pandac.PandaModules import Point3D
from strudel.model import Model, many_to_one, one_to_one, one_to_many
from strudel.planet import Planet
from strudel.units import Earth

class StarSystem(Model):
    galaxy = many_to_one(backref='systems')
    star = one_to_one(backref='system')
    ships = one_to_many(backref='system')

    def __init__(self, star):
        self.star = star
        self.galaxy = star.galaxy
        star.pos = Point3D(0,0,0)
        self.planets = []

        numorbits = 6

        inner = random.uniform(0.1, 0.3)*math.sqrt(self.star.mass)
        step = random.uniform(0.1, 0.25)
        radii = []
        for orbit in range(numorbits):
            apsis = inner + step * math.pow(2.0, orbit+1)
            period = math.sqrt(math.pow(apsis,3.0) / self.star.mass)
            eccentricity = random.expovariate(50.0)

            planet = Planet(system=self, orbiting=star, apsis=apsis,
                            period=period, eccentricity=eccentricity,
                            radius=random.uniform(star.radius/10000, star.radius/10),
                            theta=random.uniform(0,2*pi))
            self.planets.append(planet)

    @property
    def stars(self):
        return [self.star]

    def tick(self, elapsed):
        for planet in self.planets:
            planet.theta += (elapsed/(planet.period*Earth.period))*(2*pi)
            if planet.theta > 2*pi: planet.theta -= 2*pi

        for ship in self.ships:
            ship.tick(elapsed)
