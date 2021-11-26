from random import choices

import esper

from yazelc.components import Brain
from yazelc.utils.game_utils import Direction


class AISystem(esper.Processor):

    def process(self):
        for ent, brain in self.world.get_component(Brain):
            if brain.think_counter > 0:
                brain.think_counter -= 1
            if brain.think_counter == 0:
                brain.think_counter = brain.think_frames
                direction_weights = [10, 10, 10, 10, 15]
                direction_choices = list(Direction)[:4] + [None]
                brain.direction = choices(direction_choices, weights=direction_weights, k=1)[0]
