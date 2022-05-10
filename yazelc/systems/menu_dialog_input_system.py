from yazelc import dialog
from yazelc import zesper
from yazelc.components import Input, Menu, Dialog, Renderable
from yazelc.controller import Controller


class MenuDialogInputSystem(zesper.Processor):
    """ Handles input when in Menus and takes care of scrolling the text in dialog"""

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller
        self.dialog_speed_delay = 2
        self.dialog_frame_counter = 0

    def process(self):
        self.controller.process_input()

        for entity, (input_, _) in self.world.get_components(Input, Menu):
            input_.handle_input_function(entity, self.controller, self.world)

        for entity, (dialog_, renderable) in self.world.get_components(Dialog, Renderable):
            self.dialog_frame_counter += 1
            if not dialog_.idle and self.dialog_frame_counter % self.dialog_speed_delay == 0:
                surface = renderable.image
                dialog_.idle = dialog_.text.render_fitted_word(surface, dialog.DIALOG_FONT_COLOR, dialog.X_MARGIN, dialog.Y_MARGIN)
