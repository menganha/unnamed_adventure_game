import esper
from components import Animation, Renderable, Velocity, MeleeWeapon
from direction import Direction


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (anim, rend) in self.world.get_components(Animation, Renderable):
            query = self.world.try_components(ent, Velocity, MeleeWeapon)
            if query:
                vel, wpn = query
            else:
                vel = wpn = None

            if wpn and (wpn.frame_counter > 0):  # Check if it's attacking
                attacking = True
            else:
                attacking = False

            if vel and (vel.x or vel.y):  # Check if its moving
                moving = True
            else:
                moving = False

            try:
                if rend.direction == Direction.NORTH:
                    if attacking:
                        rend.image = anim.attack_up.next()
                    elif moving:
                        rend.image = anim.move_up.next()
                    else:
                        rend.image = anim.idle_up.next()
                elif rend.direction == Direction.SOUTH:
                    if attacking:
                        rend.image = anim.attack_down.next()
                    elif moving:
                        rend.image = anim.move_down.next()
                    else:
                        rend.image = anim.idle_down.next()
                elif rend.direction == Direction.WEST:
                    if attacking:
                        rend.image = anim.attack_left.next()
                    elif moving:
                        rend.image = anim.move_left.next()
                    else:
                        rend.image = anim.idle_left.next()
                else:
                    if attacking:
                        rend.image = anim.attack_right.next()
                    elif moving:
                        rend.image = anim.move_right.next()
                    else:
                        rend.image = anim.idle_right.next()

            except AttributeError:  # When no other animation is available default to idle_down
                rend.image = anim.idle_down.next()
