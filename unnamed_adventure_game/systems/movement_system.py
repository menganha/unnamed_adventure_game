import esper

from unnamed_adventure_game.components import Velocity, Position


class MovementSystem(esper.Processor):
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def process(self):
        """
         If it has a hitbox then check for collisions and modify the entity's velocity otherwise just move
        """
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y

            #  TODO: Fix condition. Still has some problems
            # pos.x = max(self.min_x, pos.x)
            # pos.y = max(self.min_y, pos.y)
            # pos.x = min(self.max_x - hitbox.rect.w, pos.x)
            # pos.y = min(self.max_y - hitbox.rect.h, pos.y)
