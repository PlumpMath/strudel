from random import random
from collections import OrderedDict
import csv

class StellarClass(object):
    main_seq_basic_freqs = {
            'O': 0.0000003,
            'B': 0.0013,
            'A': 0.006,
            'F': 0.03,
            'G': 0.076,
            'K': 0.121,
            'M': 0.7645
    }

    main_seq_luminosity_bias = {
            'O': 30000,
            'B': 27500,
            'A': 15,
            'F': 3.25,
            'G': 1.05,
            'K': 0.34,
            'M': 0.08
    }

    main_seq_proportion = 0.9

    @classmethod
    def setup(cls):
        print "Loading stellar classes..."
        # Load all 3098(!) spectral classes and their data.
        # http://isthe.com/chongo/tech/astro/HR-temp-mass-table-byhrclass.html
        cls.rows_by_spec_type = OrderedDict()
        for row in csv.DictReader(open('init/stellar_classes.csv')):
            cls.rows_by_spec_type[row['Type']] = row

        # Generate a primitive frequency table.
        # TODO: Scientific accuracy.

        main_seq_weights = {}
        non_main_weights = {}
        main_seq_total_weight = 0.0
        non_main_total_weight = 0.0

        cls.highest_radius = 0.0
        cls.lowest_radius = float("inf")

        for spec_type, row in cls.rows_by_spec_type.iteritems():
            radius = float(row['Radius'])
            if radius > cls.highest_radius: cls.highest_radius = radius
            if radius < cls.lowest_radius: cls.lowest_radius = radius

            mass = float(row['Mass'])
            if spec_type[0] in "OBAFGKM":
                ch = spec_type[0]
                lumenfactor = 1/abs(float(row['Luminosity']) - cls.main_seq_luminosity_bias[ch])
                main_seq_weights[spec_type] = cls.main_seq_basic_freqs[ch] * lumenfactor
                main_seq_total_weight += main_seq_weights[spec_type]
            else:
                non_main_weights[spec_type] = 1/mass
                non_main_total_weight += non_main_weights[spec_type]

        cls.main_seq_freqs = {}
        cls.non_main_freqs = {}

        for spec_type, weight in main_seq_weights.iteritems():
            cls.main_seq_freqs[spec_type] = weight/main_seq_total_weight

        for spec_type, weight in non_main_weights.iteritems():
            cls.non_main_freqs[spec_type] = weight/non_main_total_weight

    @classmethod
    def get(cls, spec_type):
        if not hasattr(cls, 'main_seq_freqs'):
            cls.setup()

        return StellarClass(cls.rows_by_spec_type[spec_type])

    @classmethod
    def getRandom(cls):
        if not hasattr(cls, 'main_seq_freqs'):
            cls.setup()

        if random() < cls.main_seq_proportion:
            freqs = cls.main_seq_freqs
        else:
            freqs = cls.non_main_freqs

        rand = random()
        total = 0.0
        for spec_type, freq in freqs.iteritems():
            total += freq
            if total > rand:
                return StellarClass.get(spec_type)

    def __repr__(self):
        return "<StellarClass " + self.spec_type + ">"

    def __init__(self, row):
        self.spec_type = row['Type']                                    # e.g. G2V
        self.mass = float(row['Mass'])                                # sols
        self.luminosity = float(row['Luminosity'])        # sols
        self.radius = float(row['Radius'])                        # sols
        self.temperature = float(row['Temp'])                 # surface temp, K
        self.color_index = float(row['ColorBV'])             # B-V color index
        self.magnitude = float(row['AbsMag'])                 # absolute visual magnitude
        self.bolo_magnitude = float(row['BoloCorr'])    # bolometric magnitude (total energy output)
        self.red = float(row['R'])/255.0
        self.green = float(row['G'])/255.0
        self.blue = float(row['B'])/255.0

