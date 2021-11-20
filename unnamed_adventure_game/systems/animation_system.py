import esper

from unnamed_adventure_game.components import Animation, State, Renderable
from unnamed_adventure_game.utils.game import Direction, Status


class AnimationSystem(esper.Processor):

    def process(self):
        for ent, (animation, renderable, state) in self.world.get_components(Animation, Renderable, State):

            if state.direction != state.previous_direction or state.status != state.previous_status:
                animation.frame_counter = 0

            strip = animation.strips.get(state.status, Status.IDLE).get(state.direction, Direction.SOUTH)
            animation.index = strip.frame_sequence[animation.frame_counter]
            renderable.image = strip[animation.index]

            # Advance the animation to the next frame
            animation.frame_counter += 1

            if animation.frame_counter >= len(strip.frame_sequence):
                animation.frame_counter = 0
