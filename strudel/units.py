KG = 1
KM = 1
SECOND = 1
MINUTE = 60*SECOND
HOUR = 60*MINUTE
DAY = 24*HOUR
YEAR = 365*DAY

AU = 149598000 * KM

BILLION = 1000000000

class AstroReference():
    pass

Mercury = AstroReference()
Mercury.aphelion = 0.466697*AU
Mercury.perihelion = 0.307499*AU

Earth = AstroReference()
Earth.mass = 5.9742e+24*KG
Earth.radius = 6371*KM
Earth.aphelion = 1.01671*AU
Earth.perihelion = 0.98329*AU
Earth.period = 1*YEAR

Jupiter = AstroReference()
Jupiter.mass = 317.8*Earth.mass
Jupiter.radius = 69911*KM

Pluto = AstroReference()
Pluto.mass = 1.305e+22*KG
Pluto.radius = 1153*KM
Pluto.aphelion = 48.871*AU
Pluto.perihelion = 29.657*AU

Sol = AstroReference()
Sol.radius = 6.955e+5*KM
