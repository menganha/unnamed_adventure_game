class Timer:
    def __init__(self, time: int = 0):
        self._time = time
        self._counter = time

    def tick(self):
        if self._counter > 0:
            self._counter -= 1

    def reset(self):
        self._counter = self._time

    def module(self, mod: int):
        return self._counter % mod == 0

    def has_finished(self) -> bool:
        return self._counter == 0

    def set(self, time: int):
        self._time = time
        self.reset()

    def is_set(self) -> bool:
        return self._time != 0

    def __str__(self):
        return f'Timer({self._time})'
