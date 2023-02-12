from math import isclose

from yazelc import config as cfg
from yazelc import visual_effects as vfx
from yazelc import zesper
from yazelc.components import Particle, Position, Velocity
from yazelc.event.events import BombExplosionEvent


class VisualEffectsSystem(zesper.Processor):
    """ Logic for visual effects on particles """
    ABS_TOL = 1e-2
    FRICTION = 0.75

    def process(self):
        # Particle effects
        for ent, (_, pos, vel) in self.world.get_components(Particle, Position, Velocity):
            vel.x = vel.x * self.FRICTION
            vel.y = vel.y * self.FRICTION
            if isclose(vel.x, 0, abs_tol=self.ABS_TOL) and isclose(vel.y, 0, abs_tol=self.ABS_TOL):
                self.world.delete_entity(ent)

    def on_bombexplosion(self, bomb_explosion_event: BombExplosionEvent):
        BOMB_RANGE = 20
        BOMB_PARTICLES = 60
        vfx.create_explosion(bomb_explosion_event.position, BOMB_PARTICLES, BOMB_RANGE, cfg.C_RED, self.world)
