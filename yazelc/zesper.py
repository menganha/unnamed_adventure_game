""" Module extends the esper package"""

from typing import List, Type

from esper import *


class World(World):
    """
    The class is overridden by adding state variables for entities that are "important", that is, that are referenced
    all around the code.

    Also, additional helpful methods are included
    """

    def __init__(self):
        super().__init__()
        self.player_entity_id = None
        self.camera_entity_id = None
        self.hud_entity_id = None
        self.map_layers_entity_id = []

    def remove_all_processors_except(self, excluded_processor_types: List[Type[Processor]]) -> None:
        """ No similar function on the esper Lib."""
        processors_to_remove = [proc for proc in self._processors if type(proc) not in excluded_processor_types]
        for processor in processors_to_remove:
            processor.world = None
            self._processors.remove(processor)

    def clear_processors(self):
        self._processors = []

    def clear_database(self) -> None:
        super().clear_database()
        self.player_entity_id = None
        self.camera_entity_id = None
        self.hud_entity_id = None
        self.map_layers_entity_id = []
        self.clear_processors()
