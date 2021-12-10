from yazelc import zesper

from yazelc.components import Velocity, Position, HitBox


class MovementSystem(zesper.Processor):

    def process(self):
        """
         If it has a hitbox then check for collisions and modify the entity's velocity otherwise just move
        """
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.prev_x = pos.x
            pos.prev_y = pos.y
            pos.x += vel.x
            pos.y += vel.y

        for ent, (hitbox, position, _) in self.world.get_components(HitBox, Position, Velocity):
            hitbox.rect.move_ip(round(position.x) - round(position.prev_x), round(position.y) - round(position.prev_y))
