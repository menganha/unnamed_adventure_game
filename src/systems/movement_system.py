import esper
import event_manager
from components import Velocity, Position, HitBox, Weapon

# TODO: Consider joining velocity and position under the same component.


class MovementSystem(esper.Processor):
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        event_manager.subscribe('collision', self.handle_collision)

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

    def handle_collision(self, ent_a: int, ent_b: int):
        """ Revert directions of collided objects """

        # Do not handle Weapon collisions
        if self.world.has_component(ent_a, Weapon) or self.world.has_component(ent_b, Weapon):
            return

        hitbox_a = self.world.component_for_entity(ent_a, HitBox)
        hitbox_b = self.world.component_for_entity(ent_b, HitBox)
        if self.world.has_components(ent_a, Velocity):
            hb_object = hitbox_b
            hb_subject = hitbox_a
            vel = self.world.component_for_entity(ent_a, Velocity)
            pos = self.world.component_for_entity(ent_a, Position)
        else:
            hb_object = hitbox_a
            hb_subject = hitbox_b
            vel = self.world.component_for_entity(ent_b, Velocity)
            pos = self.world.component_for_entity(ent_b, Position)

        for dir_x, dir_y in ((1, 0), (0, 1)):
            test_rect = hb_subject.rect.copy()
            test_rect.x -= vel.x * dir_x
            test_rect.y -= vel.y * dir_y
            if not test_rect.colliderect(hb_object.rect):
                hb_subject.rect = test_rect
                pos.x -= vel.x * dir_x
                pos.y -= vel.y * dir_y
                return
