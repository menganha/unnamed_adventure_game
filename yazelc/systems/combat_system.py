import logging

from yazelc import components as cmp
from yazelc import config as cfg
from yazelc import weapons
from yazelc import zesper
from yazelc.event.events import DeathEvent, HudUpdateEvent, BombExplosionEvent, DamageEvent, ExplosionEvent, DeleteEntityEvent
from yazelc.items import CollectableItemType
from yazelc.utils.game_utils import Direction
from yazelc.utils.game_utils import Status


class CombatSystem(zesper.Processor):
    TIME_TO_REMOVE_ENT_AFTER_DEATH = 15
    EXPLOSION_PARTICLES = 50
    EXPLOSION_MAX_VEL = 20
    EXPLOSION_COLOR = cfg.C_RED

    def __init__(self, player_entity_id: int):
        super().__init__()
        self.player_entity_id = player_entity_id

    def process(self):
        # Handles weapon lifetime.
        for ent, (weapon_component) in self.world.get_component(cmp.Weapon):
            weapon_component.active_timer.tick()
            if weapon_component.active_timer.has_finished():
                self.world.delete_entity(ent)

        # Handle temporal invincibility and death.
        for ent, (health) in self.world.get_component(cmp.Health):
            health.cooldown_timer.tick()
            if health.points <= 0:
                # Handling death. Using the "<" condition for cases when the inflicted damage is to big that results in negative health
                if ent == self.player_entity_id:
                    self.world.event_queue.enqueue_event(DeathEvent())
                else:
                    for component in (cmp.Brain, cmp.Health, cmp.EnemyTag, cmp.Weapon):
                        if self.world.has_component(ent, component):
                            self.world.remove_component(ent, component)

                    self.world.event_queue.enqueue_event(DeleteEntityEvent(ent), frames_delay=self.TIME_TO_REMOVE_ENT_AFTER_DEATH)
                    position = self.world.component_for_entity(ent, cmp.Position)
                    explosion_event = ExplosionEvent(position, self.EXPLOSION_PARTICLES, self.EXPLOSION_MAX_VEL, self.EXPLOSION_COLOR)
                    self.world.event_queue.enqueue_event(explosion_event, self.TIME_TO_REMOVE_ENT_AFTER_DEATH)

    def on_bomb_explosion(self, bomb_explosion_event: BombExplosionEvent):
        weapons.add_weapon_component_to_bomb(bomb_explosion_event.bomb_entity_id, self.world)

    def on_damage(self, damage_event: DamageEvent):
        # Wait for the invincibility to wear off and ignore enemy-enemy damage
        victim_health = self.world.component_for_entity(damage_event.victim_id, cmp.Health)
        attacker_weapon = self.world.component_for_entity(damage_event.attacker_id, cmp.Weapon)

        is_invincible = not victim_health.cooldown_timer.has_finished()
        is_enemy_enemy_damage = self.world.has_component(damage_event.victim_id, cmp.EnemyTag) and \
                                self.world.has_component(damage_event.attacker_id, cmp.EnemyTag)
        if is_invincible or is_enemy_enemy_damage:
            return

        # We could send an event here for entity specific handling. Like a Getting Hit event!
        if state := self.world.try_component(damage_event.victim_id, cmp.State):
            state.status = Status.HIT
            if self.world.has_component(damage_event.victim_id, cmp.Animation):
                self.world.remove_component(damage_event.victim_id, cmp.Animation)
            if self.world.has_component(damage_event.victim_id, cmp.Renderable):
                self.world.add_component(damage_event.victim_id, cmp.BlendEffect(attacker_weapon.freeze_frames))

        # if input_ := self.world.try_component(damage_event.victim_id, cmp.Input):
        #     input_.block_counter = damage_event.attacker_weapon.freeze_frames
        # TODO: Perhaps add freeze state

        victim_vel = self.world.component_for_entity(damage_event.victim_id, cmp.Velocity)
        victim_hitbox = self.world.component_for_entity(damage_event.victim_id, cmp.HitBox)
        weapon_hitbox = self.world.component_for_entity(damage_event.attacker_id, cmp.HitBox)

        rel_pos_x = victim_hitbox.centerx - weapon_hitbox.centerx
        rel_pos_y = victim_hitbox.centery - weapon_hitbox.centery
        recoil_direction = Direction.closest_diagonal_direction(rel_pos_x, rel_pos_y)
        victim_vel.x = recoil_direction.value.x * attacker_weapon.recoil_velocity
        victim_vel.y = recoil_direction.value.y * attacker_weapon.recoil_velocity

        victim_health.cooldown_timer.reset()
        victim_health.points -= attacker_weapon.damage

        if damage_event.victim_id == self.player_entity_id:
            hud_event = HudUpdateEvent(CollectableItemType.HEART, victim_health.points)
            self.world.event_queue.enqueue_event(hud_event)

        logging.info(
            f'Entity {damage_event.victim_id} has received {attacker_weapon.damage} and has {victim_health.points} health points remaining')
