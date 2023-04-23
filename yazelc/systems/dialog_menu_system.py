from yazelc import config as cfg
from yazelc import dialog_box
from yazelc import zesper
from yazelc.components import Dialog, Renderable, Position, Menu
from yazelc.controller import Button
from yazelc.event.events import InputEvent, ResumeEvent, DialogTriggerEvent, PauseEvent, SoundTriggerEvent, SoundEndEvent
from yazelc.menu import menu_box


class DialogMenuSystem(zesper.Processor):
    """ Handles all text dialog (NPC and signs) and the context menus """
    TEXT_SCROLL_SOUND_ID = 'text_scroll_1'

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
                self.world.event_queue.add(SoundEndEvent(self.TEXT_SCROLL_SOUND_ID))
                continue

            char_to_render = dialog.next_char()
            dialog.font.render_text_at(char_to_render, background, dialog.x_pos, dialog.y_pos)
            dialog.x_pos += dialog.font.space_width
            dialog.index += 1
            dialog.frame_tick = 0

            if dialog.is_at_end():
                dialog_box.add_triangle_signal(entity, self.world)
                dialog.idle = True
                self.world.event_queue.add(SoundEndEvent(self.TEXT_SCROLL_SOUND_ID))

    def on_input(self, input_event: InputEvent):

        for entity, (dialog_, renderable_) in self.world.get_components(Dialog, Renderable):
            if input_event.controller.is_button_pressed(Button.A) and dialog_.idle:
                if dialog_.is_at_end():
                    self.world.remove_component(entity, Renderable)
                    self.world.remove_component(entity, Position)
                    dialog_.index = 0
                    dialog_.index_start = 0
                    self.world.event_queue.add(ResumeEvent())
                else:
                    dialog_.idle = False
                    surface = renderable_.image
                    surface.fill(cfg.C_BLACK)
                    self.world.event_queue.add(SoundTriggerEvent(self.TEXT_SCROLL_SOUND_ID))

        # Handle Menus. TODO: Should we have a separate system to handle these??
        for entity, (menu, renderable_) in self.world.get_components(Menu, Renderable):
            menu_box.handle_menu_input(input_event, entity, menu, self.world)

    def on_dialog_trigger(self, dialog_trigger_event: DialogTriggerEvent):
        dialog = self.world.component_for_entity(dialog_trigger_event.dialog_entity_id, Dialog)
        dialog_box.create_text_box(dialog_trigger_event.dialog_entity_id, dialog, self.world)
        self.world.event_queue.add(PauseEvent())
        self.world.event_queue.add(SoundTriggerEvent(self.TEXT_SCROLL_SOUND_ID))
