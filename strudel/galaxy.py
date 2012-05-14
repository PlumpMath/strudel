from random import random, choice, gauss
from math import cos, sin, log, tanh, pi
from panda3d.core import Point3

from strudel.model import Model, one_to_many
from strudel.stellar_class import StellarClass
import cPickle as pickle
import os, sys
import logging

class GalaxyGenerator(object):
    @staticmethod
    def barred_spiral(name, numstars=10000, size=1000, deviation_from_plane=30, tightness=10, bar_to_arm=1.5, bar_star_concentration=0.2, cluster_chance = 0.02, mean_stars_per_cluster=8, cluster_spread=2):
        # Galactic coordinates are in light-years with the origin at the galaxy center.
        # Spiral pattern formula comes from: http://arxiv.org/pdf/0908.0892
        # Deviation from plane is approximated according to: http://arxiv.org/pdf/astro-ph/0507655
        # TODO: Sinusoidal dependence of said deviation by galactic longitude.
        from star import Star
        logging.info("Generating barred spiral galaxy '" + name + "'.")
        galaxy = Galaxy()
        galaxy.name = name
        galaxy.kind = "Barred Spiral"
        spec_type_count = {}

        def add_star(sclass, pos):
          if not spec_type_count.has_key(sclass.name):
            spec_type_count[sclass.name] = 1
          else:
            spec_type_count[sclass.name] += 1
          count = spec_type_count[sclass.name]

          name = sclass.name + '-' + str(count)

          Star(sclass, galaxy=galaxy, name=name, galpos=pos)

        starcount, clustercount = 0, 0
        while starcount < numstars:
          angle = random()*2*pi

          if random() < bar_star_concentration:
            # Forming in the core.
            x = choice([-1, 1])*cos(angle) + gauss(0.0, size/10)
            y = choice([-1, 1])*sin(angle) + gauss(0.0, size/10)
            z = gauss(0.0, deviation_from_plane)
            pos = Point3(x,y,z)
          else:
            magnitude = size/log(bar_to_arm*max(0.00001, tanh(angle/(2*tightness))))
            # Some random deviation from the main arm lines, decreasing density with distance.
            magnitude += gauss(0.0, size/20 + abs(magnitude)/10)
            angle += gauss(0.0, pi/16)
            x = cos(angle)
            y = sin(angle)
            pos = Point3(x,y,0) * choice([-1, 1]) * magnitude
            pos.z = gauss(0.0, deviation_from_plane)

          if random() < cluster_chance:
            # Star cluster!
            num_cluster_stars = max(3, int(gauss(mean_stars_per_cluster, mean_stars_per_cluster/4)))
            spec_type_mean = StellarClass.getRandom().name

            for j in range(0, num_cluster_stars):
              spec_type = spec_type_mean#min(len(StellarClass.rows_by_spec_type)-1, max(0, int(gauss(sclass_index_mean, 4))))
              sclass = StellarClass.get(spec_type)
              spos = Point3(pos.x + gauss(0.0, cluster_spread), pos.y + gauss(0.0, cluster_spread), pos.z)
              add_star(sclass, spos)

            starcount += num_cluster_stars
            clustercount += 1
          else:
            # A normal star placement.
            add_star(StellarClass.getRandom(), pos)
            starcount += 1

          if starcount % 1000 == 0:
            logging.info("Added %d localities and %d clusters." % (starcount, clustercount))

        return galaxy

class Galaxy(Model):
    ships = one_to_many(backref='galaxy')

    @staticmethod
    def load(name):
        logging.info("Loading Galaxy '%s'." % name)
        f = open(Galaxy.savepath(name), 'rb')
        return pickle.load(f)

    @staticmethod
    def savepath(name):
        return os.path.join(sys.path[0], "save/%s.pickle" % name)

    def __init__(self, **kwargs):
        super(Galaxy, self).__init__(**kwargs)
        self.stars = []

    def __repr__(self):
        return "<Galaxy '%s' numstars=%d>" % (self.name, len(self.stars))

    def save(self):
        logging.info("Saving %s." % self)
        output = pickle.dumps(self)
        f = open(Galaxy.savepath(self.name), 'wb')
        f.write(output)
