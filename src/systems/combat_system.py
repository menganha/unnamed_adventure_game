import logging

import components as cmp
import esper
import event_manager

"""
BIG TODO:  We have to think how to decouple the direction values from the renderable. It doesn't 
smell good. Is it possible to take it away at all? we can derive it from the current velocity values isn't it?
"""

class CombatSystem(esper.Processor):

    def __init__(self, player_entity: int):
        super().__init__()
        self.player_entity = player_entity

    def process(self):
        # == Handle weapon <-> character interaction
        for ent, (weapon, hitbox) in self.world.get_components(cmp.Weapon, cmp.HitBox):
            for victim, (health, victim_hitbox) in self.world.get_components(cmp.Health, cmp.HitBox):
                # Do not inflict self harm and enemies don't damage each other
                if (ent == victim) or \
                        (self.world.has_component(ent, cmp.EnemyTag) and self.world.has_component(victim,
                                                                                                  cmp.EnemyTag)):
                    continue
                if hitbox.rect.colliderect(victim_hitbox.rect):
                    if health.cool_down_counter == 0:  # and weapon.life_time > 0:
                        health.cool_down_counter = health.cool_down_frames
                        health.points -= weapon.damage
                        logging.info(
                            f'entity {victim} has received {weapon.damage} and has {health.points} health points remaining')

            if weapon.active_frames > 0:
                weapon.active_frames -= 1
            if weapon.active_frames == 0:
                self.world.delete_entity(ent)
                event_manager.post_event(
                    'attack')  # To signal the finishing of the attack. Maybe there's a smarter way?

        # == Handle all health components
        for ent, (health) in self.world.get_component(cmp.Health):
            if health.points <= 0:
                self.world.delete_entity(ent)
            if health.cool_down_counter > 0:
                health.cool_down_counter -= 1
