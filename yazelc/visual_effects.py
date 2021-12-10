import random
from math import radians, cos, sin

import pygame

from yazelc import components as cmp
from yazelc import zesper


def create_explosion(origin_x: int, origin_y: int, n_particles: int, max_vel: int, color: pygame.Color, world: zesper.World):
    for _ in range(n_particles):
        angle = random.randrange(0, 360, 5)
        unit_vector_x, unit_vector_y = cos(radians(angle)), sin(radians(angle))

        absolute_vel = max_vel * random.randrange(5) / 10

        vel = cmp.Velocity(unit_vector_x * absolute_vel, unit_vector_y * absolute_vel)
        pos = cmp.Position(origin_x, origin_y)
        tag = cmp.VisualEffect(color)

        world.create_entity(vel, pos, tag)
