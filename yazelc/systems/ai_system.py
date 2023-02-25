from random import choice, random

from yazelc import zesper
from yazelc.components import Brain, State, Velocity, Animation
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
                self.world.event_queue.enqueue_event()

    def on_enemydecision(self, ent_id: int, state: State, velocity: Velocity):
        if state.status == Status.MOVING:
            velocity.x = state.direction.value.x
            velocity.y = state.direction.value.y
        else:
            velocity.x = 0
            velocity.y = 0

        if state.has_changed():
            animation = self.world.component_for_entity(ent_id, Animation)
            delay = animation.delay
            image_strip = animation.strip
            self.world.add_component(ent_id, Animation(image_strip, delay=delay))
