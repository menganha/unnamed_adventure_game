from yazelc import zesper
from yazelc.components import Velocity, Position, Acceleration, HitBox


class MovementSystem(zesper.Processor):

    def process(self):
        """
        Moves all entities with positions. If it has a Hitbox component then updates their internal position as well.
        For accelerated entities it limits their minimal velocity.
        """

        for ent, (velocity, acceleration) in self.world.get_components(Velocity, Acceleration):
            velocity.x = max(velocity.x + acceleration.x, Velocity.ZERO_THRESHOLD)
            velocity.y = max(velocity.y + acceleration.x, Velocity.ZERO_THRESHOLD)

        for ent, (velocity, position) in self.world.get_components(Velocity, Position):
            position.move_ip(velocity.x, velocity.y)

            if hitbox := self.world.try_component(ent, HitBox):
                hitbox.move_ip(round(position.x) - round(position.prev_x), round(position.y) - round(position.prev_y))

        # TODO: Make a limit here for movement outside the world bounds
