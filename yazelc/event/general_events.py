from yazelc.controller import Controller
from yazelc.event.event_manager import Event
from yazelc.items import CollectableItemType
from yazelc.zesper import World


class InputEvent(Event):
    def __init__(self, controller: Controller, world: World):
        self.controller = controller
        self.world = world


class DeathEvent(Event):
    pass


class PauseEvent(Event):
    pass


class RestartEvent(Event):
    pass


class CollisionEvent(Event):

    def __init__(self, ent_1: int, ent_2: int):
        self.ent_1 = ent_1
        self.ent_2 = ent_2


class HudUpdateEvent(Event):

    def __init__(self, collectable_item_type: CollectableItemType, value: int):
        self.pickable_item_type = collectable_item_type
        self.value = value
