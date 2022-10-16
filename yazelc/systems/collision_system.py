from yazelc import zesper
from yazelc.components import Position, Velocity, HitBox
from yazelc.event import CollisionEvent


class CollisionSystem(zesper.Processor):
    """
    Processes collisions with non-moving solid entities

    The system first resolves the collisions between with solid walls and movable entities and only after it checks
    for collisions between regular hitboxes. The reasoning is that after a wall collision entities normally needs a
    repositioning which can trigger further collision with entities which have been already tested negative for
    collision. This adds a layer of complexity as one has to deal with several collision checks
    """

    def process(self):

        hitboxes = self.world.get_component(HitBox)
        for index, (ent_1, hitbox_1) in enumerate(hitboxes):
            for ent_2, hitbox_2 in hitboxes[index + 1:]:
                if hitbox_1.colliderect(hitbox_2):
                    self.events.append(CollisionEvent(ent_1, ent_2))
        # TODO: Door and Dialog box are constantly colliding

        # Resolves impenetrable hitboxes by moving objects
        impenetrable_hitboxes = [hitbox for ent, hitbox in hitboxes if hitbox.impenetrable]
        for ent, (hitbox, position, velocity) in self.world.get_components(HitBox, Position, Velocity):
            if hitbox.collidelist(impenetrable_hitboxes) != -1:
                if False:  # ent == player_ent and not collision_with_inner_hitbox():
                    pass  # some_function()
                    # collision with inner box should be a function of inflate. Check for that the inner inbox is always cenetered
                    # Check on which corner is colliding. if it's moving up, check the two upper ones. collide_with_point may help
                    # Move in the oposite of that corner and using the movement oposite to that direction.
                else:
                    # TODO: refactor this in its own function
                    for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
                        delta_x = (round(position.x) - round(position.prev_x)) * dir_x
                        delta_y = (round(position.y) - round(position.prev_y)) * dir_y
                        test_hitbox = hitbox.move(-delta_x, -delta_y)
                        if test_hitbox.collidelist(impenetrable_hitboxes) == -1:
                            hitbox.move_ip(-delta_x, -delta_y)
                            position.x = round(position.x - velocity.x * dir_x)
                            position.y = round(position.y - velocity.y * dir_y)
                            break

        # static_hitbox_rects = {ent: hitbox.rect for ent, hitbox in self.world.get_component(HitBox) if
        #                        not self.world.has_component(ent, Velocity)}
        # moving_hitboxes_entities = [element for element in self.world.get_components(HitBox, Position, Velocity)]
        #
        # # Check for collision between static hitboxes
        # static_hitbox_rects_list = list(static_hitbox_rects.items())
        # for index, (ent_1, hitbox_1) in enumerate(static_hitbox_rects_list):
        #     for ent_2, hitbox_2 in static_hitbox_rects_list[index + 1:]:
        #         if hitbox_1.colliderect(hitbox_2) and self.static_entities_are_relevant(ent_1, ent_2):
        #             event_manager.post_event(EventType.COLLISION, ent_1, ent_2)
        #
        # # Checks for collision for all static entities hitboxes against moving ones.
        # # If one moving entity collides then it resolves it by reverting the direction of movement.
        # for ent, (hitbox, position, velocity) in moving_hitboxes_entities:
        #     hitbox_collided = hitbox.rect.collidedict(static_hitbox_rects, 1)
        #     if hitbox_collided:
        #         ent_collided, _ = hitbox_collided
        #         if self.world.has_component(ent_collided, Pickable):
        #             event_manager.post_event(EventType.COLLISION, ent, ent_collided)
        #         else:  # a raw wall
        #             # if self.world.has_component(ent_collided, InteractableTag):
        #             #     event_manager.post_event(EventType.COLLISION, ent, ent_collided)
        #             for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
        #                 delta_x = (round(position.x) - round(position.prev_x)) * dir_x
        #                 delta_y = (round(position.y) - round(position.prev_y)) * dir_y
        #                 test_rect = hitbox.rect.move(-delta_x, -delta_y)
        #                 if not test_rect.collidedict(static_hitbox_rects, 1):
        #                     hitbox.rect = test_rect
        #                     position.x = round(position.x - velocity.x * dir_x)
        #                     position.y = round(position.y - velocity.y * dir_y)
        #                     break
        #
        # # Checks for collision between moving entities and posts event if they collide between each other
        # for index, (ent_1, (hitbox_1, _, _)) in enumerate(moving_hitboxes_entities):
        #     for (ent_2, (hitbox_2, _, _)) in moving_hitboxes_entities[index + 1:]:  # prevents double counting and self checking
        #         if hitbox_1.rect.colliderect(hitbox_2.rect):
        #             event_manager.post_event(EventType.COLLISION, ent_1, ent_2)
