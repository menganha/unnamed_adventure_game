import logging
from collections import deque

from cutscene.task import Task
from yazelc import zesper
from yazelc.event.events import CutsceneFinishedEvent


class CutsceneSystem(zesper.Processor):
    """ Runs list of Task types which are coroutines (generators) """

    def __init__(self, *tasks: Task):
        super().__init__()
        self.task_queue = deque(tasks)
        self.coroutine = self._get_coroutine()
        self._cutscene_finished = False if tasks else True

    def process(self, *args, **kwargs):
        if not self._cutscene_finished:
            try:
                next(self.coroutine)
            except StopIteration:
                logging.info('Finished cutscene')
                self.world.event_queue.add(CutsceneFinishedEvent())
                self._cutscene_finished = True

    def _get_coroutine(self):
        while self.task_queue:
            task = self.task_queue.popleft()
            yield from task.run(self.world)
