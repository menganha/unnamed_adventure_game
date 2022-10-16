import logging

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper
from yazelc.clock import Timer
from yazelc.event import DeathEvent, HudUpdateEvent, CollisionEvent
from yazelc.items import CollectableItemType
from yazelc.utils.game_utils import Direction
from yazelc.utils.game_utils import Status
from yazelc.visual_effects import create_explosion


class CombatSystem(zesper.Processor):
    TIME_TO_REMOVE_ENT_AFTER_DEATH = 15

    def __init__(self, player_entity_id: int):
        super().__init__()
        self.player_entity_id = player_entity_id

    def process(self):
        # Handles weapon lifetime.
        for ent, (weapon) in self.world.get_component(cmp.Weapon):
            if weapon.active_frames > 0:
                weapon.active_frames -= 1
            if weapon.active_frames == 0:
                self.world.delete_entity(ent)

        # Handle temporal invincibility and death.
        for ent, (health) in self.world.get_component(cmp.Health):
            if health.cool_down_counter > 0:
                health.cool_down_counter -= 1
            if health.points <= 0:  # Using the "<" condition for cases when the inflicted damage is to big that results in negative health
                if ent == self.player_entity_id:
                    self.events.append(DeathEvent())
                else:
                    components = []
                    position = self.world.component_for_entity(ent, cmp.Position)
                    components.append(position)
                    if renderable := self.world.try_component(ent, cmp.Renderable):
                        components.append(renderable)
                    if velocity := self.world.try_component(ent, cmp.Velocity):
                        components.append(velocity)
                    if hitbox := self.world.try_component(ent, cmp.HitBox):
                        components.append(hitbox)
                    new_ent = self.world.create_entity(*components)
                    self.world.delete_entity(ent)

                    explosion_kwargs = {'position': position, 'n_particles': 50, 'max_vel': 20, 'color': cfg.C_RED, 'world': self.world}
                    self.timers.append(Timer(self.TIME_TO_REMOVE_ENT_AFTER_DEATH, False, create_explosion, **explosion_kwargs))
                    self.timers.append(Timer(self.TIME_TO_REMOVE_ENT_AFTER_DEATH, False, self.world.delete_entity, new_ent))

    def on_collision(self, collision_event: CollisionEvent):

        if components := self.world.try_pair_signature(collision_event.ent_1, collision_event.ent_2, cmp.Health, cmp.Weapon):

            victim, victim_health, attacker, attacker_weapon = components

            # Wait for the invincibility to wear off. Don't register enemy-enemy attacks
            if victim_health.cool_down_counter != 0:
                return
            if self.world.has_component(victim, cmp.EnemyTag) and self.world.has_component(attacker, cmp.EnemyTag):
                return

            if state := self.world.try_component(victim, cmp.State):
                state.status = Status.HIT

            if input_ := self.world.try_component(victim, cmp.Input):
                input_.block_counter = attacker_weapon.freeze_frames

            victim_vel = self.world.component_for_entity(victim, cmp.Velocity)
            victim_hitbox = self.world.component_for_entity(victim, cmp.HitBox)
            weapon_hitbox = self.world.component_for_entity(attacker, cmp.HitBox)

            rel_pos_x = victim_hitbox.centerx - weapon_hitbox.centerx
            rel_pos_y = victim_hitbox.centery - weapon_hitbox.centery
            recoil_direction = Direction.closest_diagonal_direction(rel_pos_x, rel_pos_y)
            victim_vel.x = recoil_direction.value.x * attacker_weapon.recoil_velocity
            victim_vel.y = recoil_direction.value.y * attacker_weapon.recoil_velocity

            victim_health.cool_down_counter = victim_health.cool_down_frames
            victim_health.points -= attacker_weapon.damage

            if victim == self.player_entity_id:
                hud_event = HudUpdateEvent(CollectableItemType.HEART, victim_health.points)
                self.events.append(hud_event)

            logging.info(f'entity {victim} has received {attacker_weapon.damage} and has {victim_health.points} health points remaining')
