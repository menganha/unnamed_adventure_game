from yazelc import zesper

from yazelc.components import Animation, Renderable
from yazelc.utils.game_utils import Direction, Status


class AnimationSystem(zesper.Processor):

    def process(self):
        for ent, (animation, renderable) in self.world.get_components(Animation, Renderable):

            if (animation.direction != animation.previous_direction or
                    animation.status != animation.previous_status):
                animation.frame_counter = 0

            direction_strips = animation.strips.get(animation.status, animation.strips[Status.IDLE])
            strip = direction_strips.get(animation.direction, direction_strips[Direction.SOUTH])
            animation.index = strip.frame_sequence[animation.frame_counter]
            renderable.image = strip[animation.index]

            # Advance the animation to the next frame
            animation.frame_counter += 1

            if animation.frame_counter >= len(strip.frame_sequence):
                animation.frame_counter = 0
