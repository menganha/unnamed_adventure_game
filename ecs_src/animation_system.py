import esper
from components import Animation, Renderable
from direction import Direction


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (anim, rend) in self.world.get_components(Animation, Renderable):
            try:
                if rend.direction == Direction.NORTH:
                    rend.image = anim.idle_up.next()
                elif rend.direction == Direction.SOUTH:
                    rend.image = anim.idle_down.next()
                elif rend.direction == Direction.WEST:
                    rend.image = anim.idle_left.next()
                else:
                    rend.image = anim.idle_right.next()
            except AttributeError:
                # When no other animation is available default to the compulsory idle_down
                rend.image = anim.idle_down.next()

            # velocity = self.world.try_component(ent, Velocity)
            # if velocity:
            #     pass
