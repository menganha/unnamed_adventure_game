class Action:
    """
    Represent a common pattern appearing in actions that take several frames to complete and cannot be repeated until
    a cooldown time
    """

    def __init__(self, cooldown_time: int):
        self.counter = 0
        self.cooldown_time = cooldown_time

    def is_idle(self):
        return self.counter == 0

    def in_progress(self):
        return self.counter > 0

    def update(self):
        if self.in_progress():
            self.counter -= 1

    def restart(self):
        self.counter = self.cooldown_time
