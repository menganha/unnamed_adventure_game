import logging

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import zesper
from yazelc.clock import Timer
from yazelc.event.events import DeathEvent, HudUpdateEvent, BombExplosionEvent, DamageEvent
from yazelc.items import CollectableItemType
from yazelc.utils.game_utils import Direction
from yazelc.utils.game_utils import Status
from yazelc.visual_effects import create_explosion


class CombatSystem(zesper.Processor):
    TIME_TO_REMOVE_ENT_AFTER_DEATH = 15
    BOMB_DAMAGE = 3

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
                    components.append(cmp.BlendEffect(self.TIME_TO_REMOVE_ENT_AFTER_DEATH))
                    new_ent = self.world.create_entity(*components)
                    self.world.delete_entity(ent)

                    explosion_kwargs = {'position': position, 'n_particles': 50, 'max_vel': 20, 'color': cfg.C_RED, 'world': self.world}
                    self.timers.append(Timer(self.TIME_TO_REMOVE_ENT_AFTER_DEATH, False, create_explosion, **explosion_kwargs))
                    self.timers.append(Timer(self.TIME_TO_REMOVE_ENT_AFTER_DEATH, False, self.world.delete_entity, new_ent))

    def on_bombexplosion(self, bomb_explosion_event: BombExplosionEvent):
        bomb_range = 20
        hitbox = cmp.HitBox(0, 0, bomb_range * 2, bomb_range * 2)
        hitbox.center = bomb_explosion_event.position
        self.world.add_component(bomb_explosion_event.bomb_entity_id, hitbox)
        self.world.add_component(bomb_explosion_event.bomb_entity_id, cmp.Weapon(damage=self.BOMB_DAMAGE, active_frames=10))

    def on_damage(self, damage_event: DamageEvent):
        # Wait for the invincibility to wear off. Don't register enemy-enemy attacks
        if damage_event.victim_health.cool_down_counter != 0:
            return
        if self.world.has_component(damage_event.victim_id, cmp.EnemyTag) and self.world.has_component(damage_event.attacker_id,
                                                                                                       cmp.EnemyTag):
            return

        # We could send an event here for entity specific handling. Like a Getting Hit event!
        if state := self.world.try_component(damage_event.victim_id, cmp.State):
            state.status = Status.HIT
            if self.world.has_component(damage_event.victim_id, cmp.Animation):
                self.world.remove_component(damage_event.victim_id, cmp.Animation)
            if self.world.has_component(damage_event.victim_id, cmp.Renderable):
                self.world.add_component(damage_event.victim_id, cmp.BlendEffect(damage_event.attacker_weapon.freeze_frames))

        # if input_ := self.world.try_component(damage_event.victim_id, cmp.Input):
        #     input_.block_counter = damage_event.attacker_weapon.freeze_frames
        # TODO: Perhaps add freeze state

        damage_event.victim_vel = self.world.component_for_entity(damage_event.victim_id, cmp.Velocity)
        damage_event.victim_hitbox = self.world.component_for_entity(damage_event.victim_id, cmp.HitBox)
        weapon_hitbox = self.world.component_for_entity(damage_event.attacker_id, cmp.HitBox)

        rel_pos_x = damage_event.victim_hitbox.centerx - weapon_hitbox.centerx
        rel_pos_y = damage_event.victim_hitbox.centery - weapon_hitbox.centery
        recoil_direction = Direction.closest_diagonal_direction(rel_pos_x, rel_pos_y)
        damage_event.victim_vel.x = recoil_direction.value.x * damage_event.attacker_weapon.recoil_velocity
        damage_event.victim_vel.y = recoil_direction.value.y * damage_event.attacker_weapon.recoil_velocity

        damage_event.victim_health.cool_down_counter = damage_event.victim_health.cool_down_frames
        damage_event.victim_health.points -= damage_event.attacker_weapon.damage

        if damage_event.victim_id == self.player_entity_id:
            hud_event = HudUpdateEvent(CollectableItemType.HEART, damage_event.victim_health.points)
            self.events.append(hud_event)

        logging.info(
            f'Entity {damage_event.victim_id} has received {damage_event.attacker_weapon.damage} and has {damage_event.victim_health.points} health points remaining')
