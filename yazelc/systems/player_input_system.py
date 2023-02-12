from yazelc import zesper
from yazelc.event.events import InputEvent
from yazelc.player import player


class PlayerInputSystem(zesper.Processor):
    """ Uses direct callback to process the input """

    def __init__(self, player_entity_id: int):
        super().__init__()
        self.player_entity_id = player_entity_id

    def process(self):
        pass

    def on_input(self, input_event: InputEvent):
        """ Listener to the input event. Here we can add other methods of entities that react to controller events """
        player.handle_input(input_event, self.player_entity_id, self.world)
