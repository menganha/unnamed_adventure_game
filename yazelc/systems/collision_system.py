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

        # Resolves impenetrable hitboxes by moving objects
        impenetrable_static_hitboxes = [hitbox for ent, hitbox in self.world.get_component(HitBox) if hitbox.impenetrable]
        for ent, (hitbox, position, velocity) in self.world.get_components(HitBox, Position, Velocity):
            if hitbox.collidelist(impenetrable_static_hitboxes) != -1:
                if False:  # ent == player_ent and not collision_with_inner_hitbox():
                    pass  # some_function()
                    # collision with inner box should be a function of inflate. Check for that the inner inbox is always cenetered
                    # Check on which corner is colliding. if it's moving up, check the two upper ones. collide_with_point may help
                    # Move in the oposite of that corner and using the movement oposite to that direction.
                else:
                    self._resolve_collision(position, velocity, hitbox, impenetrable_static_hitboxes)

        # Everything that it is penetrable it is checked for collision after the movement checks have been resolved
        transparent_hitboxes = [(ent, hb) for ent, hb in self.world.get_component(HitBox) if not hb.impenetrable]
        for index, (ent_1, hitbox_1) in enumerate(transparent_hitboxes):
            rect_dictionary = {ent: hb for ent, hb in transparent_hitboxes[index + 1:]}  # prevents double counting and self checking
            entities_that_collided = hitbox_1.collidedictall(rect_dictionary, 1)
            for ent_2, _ in entities_that_collided:
                self.events.append(CollisionEvent(ent_1, ent_2))

    @staticmethod
    def _resolve_collision(position: Position, velocity: Velocity, hitbox: HitBox, impenetrable_hitboxes: list[HitBox]):
        """ Reverts the movement if moving object collides with hitbox """
        for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
            delta_x = (round(position.x) - round(position.prev_x)) * dir_x
            delta_y = (round(position.y) - round(position.prev_y)) * dir_y
            test_hitbox = hitbox.move(-delta_x, -delta_y)
            if test_hitbox.collidelist(impenetrable_hitboxes) == -1:
                hitbox.move_ip(-delta_x, -delta_y)
                position.x = round(position.x - velocity.x * dir_x)
                position.y = round(position.y - velocity.y * dir_y)
                break
