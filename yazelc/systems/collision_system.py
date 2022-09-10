from yazelc import event_manager
from yazelc import zesper
from yazelc.components import Position, Velocity, HitBox, Pickable, InteractorTag
from yazelc.event_type import EventType


class CollisionSystem(zesper.Processor):
    """
    Processes collisions with non-moving solid entities

    The system first resolves the collisions between with solid walls and movable entities and only after it checks
    for collisions between regular hitboxes. The reasoning is that after a wall collision entities normally needs a
    repositioning which can trigger further collision with entities which have been already tested negative for
    collision. This adds a layer of complexity as one has to deal with several collision checks

    """

    def process(self):
        static_hitbox_rects = {ent: hitbox.rect for ent, hitbox in self.world.get_component(HitBox) if
                               not self.world.has_component(ent, Velocity)}
        moving_hitboxes_entities = [element for element in self.world.get_components(HitBox, Position, Velocity)]

        for ent, (hitbox, _) in self.world.get_components(HitBox, InteractorTag):
            hitboxes_collided = hitbox.rect.collidedictall(static_hitbox_rects, 1)
            if hitboxes_collided:
                for ent_collided, _ in hitboxes_collided:
                    event_manager.post_event(EventType.COLLISION, ent, ent_collided)
            self.world.delete_entity(ent)

        # Checks for collision for all static entities against moving ones.
        # If one moving entity collides then it resolves it by reverting  the direction of movement.
        for ent, (hitbox, position, velocity) in moving_hitboxes_entities:
            hitbox_collided = hitbox.rect.collidedict(static_hitbox_rects, 1)
            if hitbox_collided:
                ent_collided, _ = hitbox_collided
                if self.world.has_component(ent_collided, Pickable):
                    event_manager.post_event(EventType.COLLISION, ent, ent_collided)
                else:  # a raw wall
                    # if self.world.has_component(ent_collided, InteractableTag):
                    #     event_manager.post_event(EventType.COLLISION, ent, ent_collided)
                    for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
                        delta_x = (round(position.x) - round(position.prev_x)) * dir_x
                        delta_y = (round(position.y) - round(position.prev_y)) * dir_y
                        test_rect = hitbox.rect.move(-delta_x, -delta_y)
                        if not test_rect.collidedict(static_hitbox_rects, 1):
                            hitbox.rect = test_rect
                            position.x = round(position.x - velocity.x * dir_x)
                            position.y = round(position.y - velocity.y * dir_y)
                            break

        # Checks for collision between moving entities and posts event if they collide between each other
        for index, (ent_1, (hitbox_1, _, _)) in enumerate(moving_hitboxes_entities):
            for (ent_2, (hitbox_2, _, _)) in moving_hitboxes_entities[index + 1:]:  # prevents double counting and self checking
                if hitbox_1.rect.colliderect(hitbox_2.rect):
                    event_manager.post_event(EventType.COLLISION, ent_1, ent_2)
