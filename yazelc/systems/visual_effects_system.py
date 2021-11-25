from math import isclose

import esper

from yazelc.components import VisualEffectTag, Position, Velocity


class VisualEffectsSystem(esper.Processor):
    """ Logic for visual effects """
    ABS_TOL = 1e-2
    FRICTION = 0.75

    def process(self):
        for ent, (_, pos, vel) in self.world.get_components(VisualEffectTag, Position, Velocity):
            vel.x = vel.x * self.FRICTION
            vel.y = vel.y * self.FRICTION
            if isclose(vel.x, 0, abs_tol=self.ABS_TOL) and isclose(vel.y, 0, abs_tol=self.ABS_TOL):
                self.world.delete_entity(ent)
