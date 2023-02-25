from yazelc import config as cfg
from yazelc import dialog_box
from yazelc import zesper
from yazelc.components import Dialog, Renderable, Position, Menu
from yazelc.controller import Button
from yazelc.event.events import InputEvent, ResumeEvent
from yazelc.menu import menu_box


class DialogMenuSystem(zesper.Processor):
    """ Handles all text dialog (NPC and signs) and the context menus """

    def __init__(self):
        super().__init__()
        self._tick_counter: int = 0

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

    def on_input(self, input_event: InputEvent):

        for entity, (dialog_, renderable_) in self.world.get_components(Dialog, Renderable):
            if input_event.controller.is_button_pressed(Button.A) and dialog_.idle:
                if dialog_.is_at_end():
                    self.world.remove_component(entity, Renderable)
                    self.world.remove_component(entity, Position)
                    dialog_.index = 0
                    dialog_.index_start = 0
                    self.world.event_queue.enqueue_event(ResumeEvent())
                else:
                    dialog_.idle = False
                    surface = renderable_.image
                    surface.fill(cfg.C_BLACK)

        for entity, (menu, renderable_) in self.world.get_components(Menu, Renderable):
            menu_box.handle_menu_input(input_event, entity, menu, self.world)
