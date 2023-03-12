from yazelc import zesper

from yazelc.components import Animation, Renderable


class AnimationSystem(zesper.Processor):

    def process(self):
        for ent, (animation, renderable) in self.world.get_components(Animation, Renderable):

            if animation.frame_counter >= len(animation.frame_sequence):
                if animation.one_loop:
                    self.world.remove_component(ent, Animation)
                    continue
                else:
                    animation.frame_counter = 0

            animation.index = animation.frame_sequence[animation.frame_counter]
            renderable.image = animation.strip[animation.index]

            # Advance the animation to the next frame
            animation.frame_counter += 1
