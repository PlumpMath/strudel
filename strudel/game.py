from pandac.PandaModules import RenderModeAttrib
from strudel.view import View
from strudel.smartcam import SmartCam
from strudel.sysview import StarSystemView
from strudel.localview import LocalView
from strudel.galaxy_view import GalaxyView
from strudel.ship import Ship

class Game(object):
    def __init__(self, base, galaxy):
        self.base = base
        self.galaxy = galaxy

        self.children = []
        self.node = base.render
        self.player = self.galaxy.ships[0]
        self.camera = SmartCam(base.cam)

        self.pressed = {}

        #self.sysview = StarSystemView(self, self.player.locality)
        #self.galview = GalaxyView(self, self.galaxy)
        self.localview = LocalView(self, self.player.locality)
        self.camera.set_focus(self.localview.view_for(self.player).node)
        self.camera.zoom_out(5000)
        self.zoom_stage = 0

        self.base.accept("wheel_up", self.zoom_in)
        self.base.accept("wheel_down", self.zoom_out)
        self.base.accept("M", self.galaxy_map)

        for key in ['w', 'a', 'd', 's']:
            self.pressed[key] = False
            self.base.accept(key, self.keydown, [key])
            self.base.accept(key+'-up', self.keyup, [key])

    def keydown(self, key):
        print "keydown: " + key
        self.pressed[key] = True

    def keyup(self, key):
        print "keyup: " + key
        self.pressed[key] = False

    def tick(self, elapsed):
        if self.pressed['w']:
            self.player.accelerate(1*elapsed)
        if self.pressed['s']:
            self.player.accelerate(-1*elapsed)
        if self.pressed['a']:
            self.player.turn_left(10*elapsed)
        if self.pressed['d']:
            self.player.turn_right(10*elapsed)

        self.player.tick(elapsed)

    def zoom_in(self):
        if self.zoom_stage <= -5:
            self.camera.zoom_in(100)
            self.localview.distance_scale *= 1.5
            self.localview.render()
        else:
            self.camera.zoom_in()

        self.zoom_stage += 1

    def zoom_out(self):
        if self.zoom_stage <= -5:
            self.camera.zoom_out(100)
            self.localview.distance_scale *= (1/1.5)
            self.localview.render()
        else:
            self.camera.zoom_out()


        self.zoom_stage -= 1

    def galaxy_map(self):
        pass

