from itertools import permutations

import esper
import event_manager
from components import Health, Weapon, Enemy

"""
BIG TODO:  We have to think how to decouple the direction values from the renderable. It doesn't 
smell good. Is it possible to take it away at all? we can derive it from the current velocity values isn't it?
"""


class CombatSystem(esper.Processor):

    def __init__(self, player_entity: int):
        super().__init__()
        self.player_entity = player_entity
        event_manager.subscribe('collision', self.handle_collision)

    def process(self):
        for ent, (weapon) in self.world.get_component(Weapon):
            if weapon.life_time > 0:
                weapon.life_time -= 1
            elif weapon.life_time == 0:
                self.world.delete_entity(ent)
                event_manager.post_event('attack')

        for ent, (health) in self.world.get_component(Health):
            if health.frame_counter > 0:
                health.frame_counter -= 1

    def handle_collision(self, ent_a: int, ent_b: int):
        """
        Handles two possible cases:
            1. Entity with Weapon component vs entity with Health
            2. Enemy entity vs player entity
        """
        for ent_attacking, ent_hit in permutations((ent_a, ent_b), 2):
            weapon = self.world.try_component(ent_attacking, Weapon)
            health = self.world.try_component(ent_hit, Health)
            if weapon and health:
                if health.frame_counter == 0 and weapon.life_time > 0:
                    health.frame_counter = health.cool_down_frames
                    health.points -= weapon.damage
                    if health.points == 0:
                        self.world.delete_entity(ent_hit)
                return

        for ent_attacking, ent_hit in permutations((ent_a, ent_b), 2):
            is_player = True if ent_attacking == self.player_entity else False
            enemy = self.world.try_components(ent_hit, Enemy)
            if is_player and enemy:
                self.world.component_for_entity(self.player_entity, Health).points -= enemy.damage
                return
