from yazelc import dialog_box
from yazelc import event_manager
from yazelc import zesper
from yazelc.components import Dialog, InteractorTag, Renderable
from yazelc.event_type import EventType


class DialogSystem(zesper.Processor):
    """ Handles all text dialog. NPC and signs """

    def __init__(self):
        self.tick_counter = 0
        event_manager.subscribe(EventType.COLLISION, self.on_collision)

    def process(self):
        for entity, (dialog, renderable_cmp) in self.world.get_components(Dialog, Renderable):
            if dialog.idle:
                continue

            if dialog.frame_tick < dialog.frame_delay:
                dialog.frame_tick += 1
                continue

            background = renderable_cmp.image
            width, height = background.get_size()
            line_spacing = dialog.font.char_height + dialog_box.DELTA_LINE_SPACING

            if dialog.index == 0:
                dialog.x_pos, dialog.y_pos = dialog_box.X_MARGIN, dialog.font.char_height + dialog_box.Y_MARGIN
            if not dialog.font.fits_on_box(dialog.current_sentence(), width):
                dialog.y_pos += line_spacing
                dialog.x_pos = dialog_box.X_MARGIN
                dialog.index_start = dialog.index
            if dialog.y_pos >= height - dialog_box.Y_MARGIN:
                dialog_box.add_triangle_signal(entity, self.world)
                dialog.x_pos, dialog.y_pos = dialog_box.X_MARGIN, dialog.font.char_height + dialog_box.Y_MARGIN
                dialog.index_start = dialog.index
                dialog.idle = True
                continue

            char_to_render = dialog.next_char()
            dialog.font.render_text_at(char_to_render, background, dialog.x_pos, dialog.y_pos)
            dialog.x_pos += dialog.font.space_width
            dialog.index += 1
            dialog.frame_tick = 0

            if dialog.is_at_end():
                dialog_box.add_triangle_signal(entity, self.world)
                dialog.idle = True

    def on_collision(self, ent1: int, ent2: int):
        """ Handles collision when interacting with entities with the Dialog component """
        if components := self.world.try_pair_signature(ent1, ent2, InteractorTag, Dialog):
            interactor_entity_id, _, dialog_entity_id, dialog = components
            dialog_box.create_text_box(dialog_entity_id, dialog, self.world)
            event_manager.post_event(EventType.PAUSE)
