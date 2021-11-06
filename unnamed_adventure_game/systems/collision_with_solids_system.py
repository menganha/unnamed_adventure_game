import esper

import unnamed_adventure_game.components as cmp
from unnamed_adventure_game import event_manager
from unnamed_adventure_game.event_type import EventType


class CollisionWithSolidsSystem(esper.Processor):
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
            hitbox.rect.x = position.x - int(hitbox.scale_offset / 2)
            hitbox.rect.y = position.y - int(hitbox.scale_offset / 2)

            if hitbox.rect.collidelist(static_hitboxes) != -1:
                for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
                    test_rect = hitbox.rect.move(-velocity.x * dir_x, -velocity.y * dir_y)
                    if test_rect.collidelist(static_hitboxes) == -1:
                        hitbox.rect = test_rect
                        position.x -= velocity.x * dir_x
                        position.y -= velocity.y * dir_y
                        break

        # Checks for collision between non-wall entities and posts event if they collide between each other
        hitboxes = [(ent, hitbox) for ent, hitbox in self.world.get_component(cmp.HitBox)
                    if not self.world.has_component(ent, cmp.WallTag)]

        for index, (ent_1, hitbox_1) in enumerate(hitboxes):
            for ent_2, hitbox_2 in hitboxes[index + 1:]:  # prevents double counting and self checking
                if hitbox_1.rect.colliderect(hitbox_2.rect):
                    event_manager.post_event(EventType.COLLISION, ent_1, ent_2)
