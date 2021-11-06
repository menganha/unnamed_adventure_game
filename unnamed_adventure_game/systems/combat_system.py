import logging
from math import copysign

import esper

import unnamed_adventure_game.components as cmp
from unnamed_adventure_game import event_manager
from unnamed_adventure_game.event_type import EventType
from unnamed_adventure_game.utils.esper import try_pair_signature
from unnamed_adventure_game.utils.game import Status

"""
BIG TODO:  We have to think how to decouple the direction values from the renderable. It doesn't 
smell good. Is it possible to take it away at all? we can derive it from the current velocity values isn't it?
"""


class CombatSystem(esper.Processor):

    def __init__(self, player_entity: int):
        super().__init__()
        self.player_entity = player_entity
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        # Handles weapon lifetime.
        for ent, (weapon, hitbox) in self.world.get_components(cmp.Weapon, cmp.HitBox):
            if weapon.active_frames > 0:
                weapon.active_frames -= 1
            if weapon.active_frames == 0:
                self.world.delete_entity(ent)
                # a = self.world.component_for_entity(ent, cmp.BeingState)# .state = State.IDLE
                # print('yes')

        # Handle temporal invincibility and death.
        for ent, (health) in self.world.get_component(cmp.Health):
            if health.points <= 0:
                self.world.delete_entity(ent)
            if health.cool_down_counter > 0:
                health.cool_down_counter -= 1

    def on_collision(self, ent1: int, ent2: int):

        if components := try_pair_signature(self.world, ent1, ent2, cmp.Health, cmp.Weapon):

            victim, victim_health, attacker, attacker_weapon = components

            # Wait for the invincibility to wear off. Don't register enemy-enemy attacks
            if victim_health.cool_down_counter != 0:
                return
            if self.world.has_component(victim, cmp.EnemyTag) and self.world.has_component(attacker, cmp.EnemyTag):
                return

            self.world.component_for_entity(victim, cmp.State).status = Status.IDLE

            input_ = self.world.component_for_entity(victim, cmp.Input)
            input_.block_counter = attacker_weapon.freeze_frames

            vel = self.world.component_for_entity(victim, cmp.Velocity)
            vel.x = copysign(3, -vel.x)  # TODO: Make it global or set in a component
            vel.y = 0

            victim_health.cool_down_counter = victim_health.cool_down_frames
            victim_health.points -= attacker_weapon.damage

            logging.info(f'entity {victim} has received {attacker_weapon.damage} and has {victim_health.points} health points remaining')
