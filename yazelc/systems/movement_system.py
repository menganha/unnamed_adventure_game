from yazelc import zesper
from yazelc.components import Velocity, Position, HitBox


class MovementSystem(zesper.Processor):

    def process(self):
        """
         Moves all entities with positions. If it has a Hitbox component, then updates their internal position as well
        """
        for ent, (velocity, position) in self.world.get_components(Velocity, Position):
            position.prev_x = position.x
            position.prev_y = position.y
            position.x += velocity.x
            position.y += velocity.y

            if hitbox := self.world.try_component(ent, HitBox):
                hitbox.rect.move_ip(round(position.x) - round(position.prev_x), round(position.y) - round(position.prev_y))

        # TODO: Make a limit here for movement outside the world bounds
