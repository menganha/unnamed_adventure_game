import esper

import unnamed_adventure_game.components as cmp


class CollisionWithSolidsSystem(esper.Processor):
    """ Processes collisions with non-moving solid entities """

    def process(self):
        static_hitboxes = [hitbox.rect for _, (hitbox, _) in self.world.get_components(cmp.HitBox, cmp.WallTag)]

        for ent, (hitbox, position, velocity) in self.world.get_components(cmp.HitBox, cmp.Position, cmp.Velocity):
            hitbox.rect.x = position.x - int(hitbox.scale_offset / 2)
            hitbox.rect.y = position.y - int(hitbox.scale_offset / 2)

            if hitbox.rect.collidelist(static_hitboxes) != -1:
                # Checks if the collisions when reverting the directions of movement and resolves it
                for dir_x, dir_y in ((1, 0), (0, 1), (1, 1)):
                    test_rect = hitbox.rect.move(-velocity.x * dir_x, -velocity.y * dir_y)
                    if test_rect.collidelist(static_hitboxes) == -1:
                        hitbox.rect = test_rect
                        position.x -= velocity.x * dir_x
                        position.y -= velocity.y * dir_y
                        break
