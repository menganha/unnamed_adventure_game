import esper

from yazelc import components as cmp
from yazelc import event_manager
from yazelc.event_type import EventType


class CollisionSystem(esper.Processor):
    """
    Processes collisions with non-moving solid entities

    The system first resolves the collisions between with solid walls and movable entities and only after it checks
    for collisions between regular hitboxes. The reasoning is that after a wall collision entities normally needs a
    repositioning which can trigger further collision with entities which have been already tested negative for
    collision. This adds a layer of complexity as one has to deal with several collision checks

    """

    def process(self):
        static_hitboxes = [hitbox.rect for _, (hitbox, _) in self.world.get_components(cmp.HitBox, cmp.WallTag)]

        # Checks for collision with wall entities. If it collides it resolves it by reverting the direction of movement
        for ent, (hitbox, position, velocity) in self.world.get_components(cmp.HitBox, cmp.Position, cmp.Velocity):

            if hitbox.rect.collidelist(static_hitboxes) != -1:
                for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
                    delta_x = (round(position.x) - round(position.prev_x)) * dir_x
                    delta_y = (round(position.y) - round(position.prev_y)) * dir_y
                    test_rect = hitbox.rect.move(-delta_x, -delta_y)
                    if test_rect.collidelist(static_hitboxes) == -1:
                        hitbox.rect = test_rect
                        position.x = round(position.x - velocity.x * dir_x)
                        position.y = round(position.y - velocity.y * dir_y)
                        break

        # Checks for collision between non-wall entities and posts event if they collide between each other
        hitboxes = [(ent, hitbox) for ent, hitbox in self.world.get_component(cmp.HitBox)
                    if not self.world.has_component(ent, cmp.WallTag)]

        for index, (ent_1, hitbox_1) in enumerate(hitboxes):
            for ent_2, hitbox_2 in hitboxes[index + 1:]:  # prevents double counting and self checking
                if hitbox_1.rect.colliderect(hitbox_2.rect):
                    event_manager.post_event(EventType.COLLISION, ent_1, ent_2)
