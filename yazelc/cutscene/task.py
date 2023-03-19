from abc import ABC, abstractmethod
from collections.abc import Generator

from yazelc.zesper import World


class Task(ABC):

    def run(self, world: World) -> Generator[None, None, None]:
        """ Coroutine """
        while not self.is_finished(world):
            self.update(world)
            yield

    @abstractmethod
    def update(self, world: World):
        """ should update the task"""
        pass

    @abstractmethod
    def is_finished(self, world: World) -> bool:
        pass
