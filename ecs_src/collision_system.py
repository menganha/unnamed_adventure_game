import esper
from components import Velocity, Renderable, Position


class CollisionSystem(esper.Processor):
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, rend, pos) in self.world.get_components(Velocity, Renderable, Position):
            # Update the Renderable Component's position by it's Velocity:
            pos.x += vel.x
            pos.y += vel.y
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it tries to go outside:
            pos.x = max(self.min_x, pos.x)
            pos.y = max(self.min_y, pos.y)
            pos.x = min(self.max_x - rend.w, pos.x)
            pos.y = min(self.max_y - rend.h, pos.y)
