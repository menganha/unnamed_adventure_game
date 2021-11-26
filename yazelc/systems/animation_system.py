import esper

from yazelc.components import Animation, State, Renderable
from yazelc.utils.game_utils import Direction, Status


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (animation, renderable, state) in self.world.get_components(Animation, Renderable, State):

            if state.direction != state.previous_direction or state.status != state.previous_status:
                animation.frame_counter = 0

            direction_strips = animation.strips.get(state.status, animation.strips[Status.IDLE])
            strip = direction_strips.get(state.direction, direction_strips[Direction.SOUTH])
            animation.index = strip.frame_sequence[animation.frame_counter]
            renderable.image = strip[animation.index]

            # Advance the animation to the next frame
            animation.frame_counter += 1

            if animation.frame_counter >= len(strip.frame_sequence):
                animation.frame_counter = 0
