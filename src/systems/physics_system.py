import components as cmp
import esper
import event_manager


#
# TODO: Big one: Loop only over components that have a velocity (non-static) Otherwise it is a waste of resources
#


class PhysicsSystem(esper.Processor):

    def process(self):
        components = self.world.get_components(cmp.HitBox, cmp.Position)
        # First update all hitbox rects to it's entity's position
        for ent, (hitbox, position) in components:
            hitbox.rect.x = position.x - int(hitbox.scale_offset / 2)
            hitbox.rect.y = position.y - int(hitbox.scale_offset / 2)

        # Now resolve all possible rect collisions
        for ent, (hitbox, position) in components:
            other_components = [(other_ent, other_hitbox) for other_ent, (other_hitbox, _) in components
                                if ent != other_ent]
            index = hitbox.rect.collidelist([hb.rect for _, hb in other_components])
            if index != -1:
                other_ent = other_components[index][0]
                event_manager.post_event('collision', ent, other_ent)
