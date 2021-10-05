import esper
from components import Velocity, Position, HitBox


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

            hitbox = self.world.try_component(ent, HitBox)
            if hitbox:
                hitbox.rect.x = pos.x + vel.x + hitbox.x_offset
                hitbox.rect.y = pos.y + vel.y + hitbox.y_offset
                rects = [hb.rect for hb_ent, hb in self.world.get_component(HitBox) if hb_ent != ent]
                index = hitbox.rect.collidelist(rects)
                if index != -1:
                    for direction in ((1, 0), (0, 1)):
                        test_rect = hitbox.rect.copy()
                        test_rect.x -= vel.x * direction[0]
                        test_rect.y -= vel.y * direction[1]
                        if not test_rect.colliderect(rects[index]):
                            vel.x *= direction[1]
                            vel.y *= direction[0]
                            hitbox.rect.x = pos.x + vel.x + hitbox.x_offset
                            hitbox.rect.y = pos.y + vel.y + hitbox.y_offset
                            break
            pos.x += vel.x
            pos.y += vel.y

            # # TODO: Fix condition. Still has some problems
            # pos.x = max(self.min_x, pos.x)
            # pos.y = max(self.min_y, pos.y)
            # pos.x = min(self.max_x - hitbox.rect.w, pos.x)
            # pos.y = min(self.max_y - hitbox.rect.h, pos.y)
