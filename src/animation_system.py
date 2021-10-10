import esper
import event_manager
from components import Animation, Renderable, Velocity
from direction import Direction


class AnimationSystem(esper.Processor):

    def __init__(self):
        super().__init__()
        self.is_attacking = False
        event_manager.subscribe('attack', self.on_attack)

    def process(self):
        for ent, (anim, rend) in self.world.get_components(Animation, Renderable):

            vel = self.world.try_component(ent, Velocity)
            if vel and (vel.x or vel.y):  # Check if its moving
                moving = True
            else:
                moving = False

            try:
                if rend.direction == Direction.NORTH:
                    if self.is_attacking:
                        rend.image = anim.attack_up.next()
                    elif moving:
                        rend.image = anim.move_up.next()
                    else:
                        rend.image = anim.idle_up.next()
                elif rend.direction == Direction.SOUTH:
                    if self.is_attacking:
                        rend.image = anim.attack_down.next()
                    elif moving:
                        rend.image = anim.move_down.next()
                    else:
                        rend.image = anim.idle_down.next()
                elif rend.direction == Direction.WEST:
                    if self.is_attacking:
                        rend.image = anim.attack_left.next()
                    elif moving:
                        rend.image = anim.move_left.next()
                    else:
                        rend.image = anim.idle_left.next()
                else:
                    if self.is_attacking:
                        rend.image = anim.attack_right.next()
                    elif moving:
                        rend.image = anim.move_right.next()
                    else:
                        rend.image = anim.idle_right.next()

            except AttributeError:  # When no other animation is available default to idle_down
                rend.image = anim.idle_down.next()

    def on_attack(self):
        self.is_attacking = not self.is_attacking
