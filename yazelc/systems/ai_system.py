from random import choice, random

from yazelc import zesper
from yazelc.components import Brain, State, Velocity, Animation
from yazelc.event.events import EnemyDecisionEvent
from yazelc.utils.game_utils import Direction, Status


class AISystem(zesper.Processor):

    def process(self):
        for ent, (brain, state) in self.world.get_components(Brain, State):
            state.update()

            if brain.block_timer.is_set():
                if brain.block_timer.has_finished():
                    brain.block_timer.set(0)
                    if animation := self.world.try_component(ent, Animation):
                        animation.resume()
                brain.block_timer.tick()

            if brain.timer.has_finished() and not brain.block_timer.is_set():
                brain.timer.reset()
                self.world.event_queue.enqueue_event(EnemyDecisionEvent(ent))

            brain.timer.tick()

    def on_enemy_decision(self, enemy_decision_event: EnemyDecisionEvent):
        """ One of several more behaviors for enemies """

        state = self.world.component_for_entity(enemy_decision_event.enemy_id, State)
        velocity = self.world.component_for_entity(enemy_decision_event.enemy_id, Velocity)

        direction_choices = list(Direction)[:4]
        state.direction = choice(direction_choices)
        state.status = Status.IDLE if random() < 0.5 else Status.MOVING  # TODO: Do we need statuses at all????!!

        if state.status == Status.MOVING:
            velocity.x = state.direction.value.x
            velocity.y = state.direction.value.y
        else:
            velocity.x = 0
            velocity.y = 0
