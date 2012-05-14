from math import pi, sin, cos
from pandac.PandaModules import VBase3, Point3D, VBase3D
from strudel.model import Model, many_to_one
from strudel.view import View
from strudel.units import AU

class MoveState(object):
    NORMAL = 'normal'
    SHORT_JUMP = 'short_jump'

class Ship(Model):
    galaxy = many_to_one(backref='ships')
    locality = many_to_one(backref='ships')

    def __init__(self, **kwargs):
        Model.__init__(self, **kwargs)
        self.pos = Point3D(0,0,0)
        self.hpr = VBase3(0,0,0)
        self.movestate = MoveState.NORMAL
        self.velocity = VBase3D(0,0,0)
        self.destination = None
        self.short_jump_speed = 0.1*AU # per second

    @property
    def facing(self):
        """Calculates a unit vector based on the current HPR."""
        heading_rad = self.hpr.y * pi/180
        vec = VBase3D(sin(heading_rad), cos(heading_rad), 0)
        vec.normalize()
        return vec

    def short_jump(self, dest):
        self.movestate = MoveState.SHORT_JUMP
        self.destination = dest
        self.emit('short_jump', dest)

    def tick(self, elapsed):
        if self.movestate == MoveState.SHORT_JUMP:
            remaining = (self.destination-self.pos)
            if remaining.length() < self.short_jump_speed:
                self.movestate = MoveState.NORMAL
                self.pos = self.destination
                self.destination = None
                self.emit('short_jump_end')
            else:
                remaining.normalize()
                self.move(self.pos + remaining*self.short_jump_speed)
        else:
            self.move(self.pos + (self.velocity * elapsed))

    def accelerate(self, amount):
        self.velocity += (self.facing * amount)

    def turn_right(self, degrees):
        self.hpr.y = (self.hpr.y + degrees) % 360
        self.emit('reorient')

    def turn_left(self, degrees):
        self.hpr.y = (self.hpr.y - degrees) % 360
        print self.hpr.y
        self.emit('reorient')

    def move(self, newpos, *args):
        if len(args) > 0: # We're being passed coordinates.
            newpos = Point3D(newpos, args[0], args[1])
        self.pos = newpos
        self.emit('reposition')


class ShipView(View):
    def __init__(self, parent, ship, **kwargs):
        super(ShipView, self).__init__(parent, ship, **kwargs)
        node = self.base.loader.loadModel("model/ship")
        tex = self.base.loader.loadTexture("texture/ship.png")
        node.setTexture(tex)
        node.setHpr(0, 90, 0)
        node.setScale(1/node.getBounds().getRadius())
        node.flattenLight()
        node.setTransparency(1)
        node.reparentTo(parent.node)
        self.node = node

class ShipIconView(View):
    def __init__(self, parent, ship, **kwargs):
        super(ShipIconView, self).__init__(parent, ship, **kwargs)
        node = self.base.loader.loadModel("model/plane")
        tex = self.base.loader.loadTexture("texture/ship_icon.png")
        node.setTexture(tex)
        node.setHpr(0, 90, 0)
        node.setScale(1/node.getBounds().getRadius())
        node.flattenLight()
        node.setTransparency(1)
        node.reparentTo(parent.node)
        self.node = node
