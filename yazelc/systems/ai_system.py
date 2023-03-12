from random import choice, random

from yazelc import zesper
from yazelc.components import Brain, State, Velocity, Animation, Enemy
from yazelc.event.events import EnemyDecisionEvent
from yazelc.utils.game_utils import Direction, Status


class AISystem(zesper.Processor):

    def process(self):
        for ent, (brain, state) in self.world.get_components(Brain, State):
            state.update()

            if brain.block_timer.is_set():
                if brain.block_timer.has_finished():
                    brain.block_timer.set(0)
                    brain.timer.end()
                brain.block_timer.tick()


            if brain.timer.has_finished() and not brain.block_timer.is_set():
                brain.timer.reset()
                self.world.event_queue.enqueue_event(EnemyDecisionEvent(ent, brain.behaviour_type))

            brain.timer.tick()

    def on_enemy_decision(self, enemy_decision_event: EnemyDecisionEvent):
        """ One of several more behaviors for enemies """

        state = self.world.component_for_entity(enemy_decision_event.enemy_id, State)
        velocity = self.world.component_for_entity(enemy_decision_event.enemy_id, Velocity)

        direction_choices = list(Direction)[:4]
        state.direction = choice(direction_choices)
        state.status = Status.IDLE if random() < 0.7 else Status.WALKING  # TODO: Do we need statuses at all????!!

        # This considers all enemies have animations!
        enemy_type = self.world.component_for_entity(enemy_decision_event.enemy_id, Enemy).type
        animation_identifier = self.world.resource_manager.get_animation_identifier(enemy_type, state.status, state.direction)
        animation_strip = self.world.resource_manager.get_animation_strip(animation_identifier)
        animation = Animation.from_delay(animation_strip,
                                         10)  # TODO: This is hardcoded. Berrry bad! Maybe include the frame information on the animation stripe
        self.world.add_component(enemy_decision_event.enemy_id, animation)

        if state.status == Status.WALKING:
            velocity.x = state.direction.value.x
            velocity.y = state.direction.value.y
        else:
            velocity.x = 0
            velocity.y = 0
