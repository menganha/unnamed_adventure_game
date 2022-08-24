from yazelc import dialog
from yazelc import event_manager
from yazelc import text_renderer
from yazelc import zesper
from yazelc.components import Dialog, InteractorTag, Renderable
from yazelc.event_type import EventType


class DialogSystem(zesper.Processor):
    """ Handles all text dialog. NPC and signs """
    TICK_LIMIT = 10  # Represents how many frames to wait until a word is printed to screen

    def __init__(self):
        event_manager.subscribe(EventType.COLLISION, self.on_collision)
        self.tick_counter = 0

    def process(self):
        for entity, (dialog_cmp, renderable_cmp) in self.world.get_components(Dialog, Renderable):
            if dialog_cmp.idle:
                continue

            if dialog_cmp.frame_tick < dialog_cmp.frame_delay:
                dialog_cmp.frame_tick += 1
                continue

            background = renderable_cmp.image
            font = self.world.resource_manager.get_font('Anonymous Pro')
            text_to_render = dialog.text_to_render(dialog_cmp)
            fitted = text_renderer.render_fitted_word(font, text_to_render, background, dialog.DIALOG_FONT_COLOR, dialog.X_MARGIN,
                                                      dialog.Y_MARGIN)
            if not fitted:
                dialog.add_blinking_signal(entity, self.world)
                dialog_cmp.index_start = dialog_cmp.index
                dialog_cmp.idle = True

            dialog_cmp.index += 1
            dialog_cmp.frame_tick = 0

            if dialog.is_at_end(dialog_cmp):
                dialog.add_blinking_signal(entity, self.world)
                dialog_cmp.idle = True

    def on_collision(self, ent1: int, ent2: int):
        """ Handles collision when interacting with entities with the Dialog component """
        if components := self.world.try_pair_signature(ent1, ent2, InteractorTag, Dialog):
            interactor_entity_id, _, dialog_entity_id, dialog_cmp = components
            dialog.create_text_box(dialog_entity_id, dialog_cmp, self.world)
            event_manager.post_event(EventType.PAUSE)
