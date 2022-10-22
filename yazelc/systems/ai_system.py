from random import choice, random

from yazelc import zesper
from yazelc.components import Brain, State
from yazelc.utils.game_utils import Direction, Status


class AISystem(zesper.Processor):

    def process(self):
        for ent, (brain, state) in self.world.get_components(Brain, State):
            state.update()
            if brain.think_counter > 0:
                brain.think_counter -= 1
            if brain.think_counter == 0:
                brain.think_counter = brain.think_frames
                direction_choices = list(Direction)[:4]
                state.direction = choice(direction_choices)
                state.status = Status.IDLE if random() < 0.5 else Status.MOVING
