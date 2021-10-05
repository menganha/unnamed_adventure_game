import esper
from components import Animation, Renderable, Velocity


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (anim, rend) in self.world.get_components(Animation, Renderable):
            rend.image = anim.idle_down.next()
            # velocity = self.world.try_component(ent, Velocity)
            # if velocity:
            #     pass
