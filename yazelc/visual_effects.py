import random

from pygame import Color, Vector2

from yazelc import components as cmp
from yazelc import zesper


def create_explosion(position: tuple[int, int], n_particles: int, max_vel: int, color: Color, world: zesper.World):
    for _ in range(n_particles):
        absolute_vel = max_vel * random.randrange(5) / 10
        angle = random.randrange(0, 360, 5)
        vel_vector = Vector2()
        vel_vector.from_polar((absolute_vel, angle))

        vel = cmp.Velocity(vel_vector.x, vel_vector.y)
        pos = cmp.Position(*position)
        tag = cmp.Particle(color)

        world.create_entity(vel, pos, tag)
