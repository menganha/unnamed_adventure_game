import pygame

from yazelc import dialog
from yazelc import event_manager
from yazelc import zesper
from yazelc.components import Dialog, InteractorTag
from yazelc.event_type import EventType


class DialogSystem(zesper.Processor):
    """ Handles all text dialog. NPC and signs """

    def __init__(self):
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        pass  # Something should be cleaned up here

    def on_collision(self, ent1: int, ent2: int):
        """ Handles collision when interacting with entities with the Dialog component """
        if components := self.world.try_pair_signature(ent1, ent2, InteractorTag, Dialog):
            interactor_entity_id, _, dialog_entity_id, text_dialog = components
            # Create some type of menu or thing that can be controlled
            dialog.create_dialog(dialog_entity_id, self.world)
            pygame.event.post(pygame.event.Event(EventType.PAUSE.value))
