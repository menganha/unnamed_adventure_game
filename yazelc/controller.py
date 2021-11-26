import abc
from enum import Enum, auto


class Button(Enum):
    """
    Buttons on a controller base on the classic SNES controller.
    These are the only inputs the game recognizes
    """
    A = auto()
    B = auto()
    X = auto()
    Y = auto()
    L = auto()
    R = auto()
    START = auto()
    SELECT = auto()
    UP = auto()
    LEFT = auto()
    DOWN = auto()
    RIGHT = auto()


class Controller(abc.ABC):
    """ Main interface to game input """

    @abc.abstractmethod
    def process_input(self):
        pass

    @abc.abstractmethod
    def is_button_down(self, button: Button) -> bool:
        pass

    @abc.abstractmethod
    def is_button_pressed(self, button: Button) -> bool:
        pass

    @abc.abstractmethod
    def is_button_released(self, button: Button) -> bool:
        pass
