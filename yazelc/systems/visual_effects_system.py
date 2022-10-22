from math import isclose

from yazelc import zesper
from yazelc.components import Particle, Position, Velocity


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
