from ecs_src import esper
from ecs_src.components import Velocity, Renderable, Position, HitBox


class MovementSystem(esper.Processor):
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def process(self):
        for ent, (vel, rend, pos) in self.world.get_components(Velocity, Renderable, Position):
            # If it has a hitbox then check for collisions
            hitbox = self.world.try_component(ent, HitBox)
            if hitbox:
                hitbox.rect.x += vel.x
                hitbox.rect.y += vel.y
                rects = [hb.rect for hb_ent, hb in self.world.get_component(HitBox) if hb_ent != ent]
                index = hitbox.rect.collidelist(rects)
                if index != -1:
                    for direction in ((1, 0), (0, 1)):
                        test_rect = hitbox.rect.copy()
                        test_rect.x -= vel.x * direction[0]
                        test_rect.y -= vel.y * direction[1]
                        if not test_rect.colliderect(rects[index]):
                            hitbox.rect = test_rect
                            break
                pos.x = hitbox.rect.x
                pos.y = hitbox.rect.y
            else:
                pos.x += vel.x
                pos.y += vel.y

            # TODO: Fix condition. Still has some problems
            pos.x = max(self.min_x, pos.x)
            pos.y = max(self.min_y, pos.y)
            pos.x = min(self.max_x - hitbox.rect.w, pos.x)
            pos.y = min(self.max_y - hitbox.rect.h, pos.y)
