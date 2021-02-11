import pygame


class Control:
    """
    Control Input
    """

    def __init__(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.attack = False
        self.attack_locked = False
        self.shoot = False
        self.shoot_locked = False
        self.close_window = False
        self.has_gamepad = False
        self.gamepad = None
        self.check_if_gamepad()

    def fetch_input(self):
        if self.attack_locked:
            self.attack = False
        if self.shoot_locked:
            self.shoot = False
        if self.has_gamepad:
            self._handle_gamepad()
        else:
            self._handle_keyboard()

    def check_if_gamepad(self):
        pygame.joystick.init()
        self.has_gamepad = pygame.joystick.get_count()
        if self.has_gamepad:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
        else:
            pygame.joystick.quit()

    def _handle_gamepad(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window = True
        self.right = round(self.gamepad.get_axis(0)) == 1
        self.left = round(self.gamepad.get_axis(0)) == -1
        self.up = round(self.gamepad.get_axis(1)) == -1
        self.down = round(self.gamepad.get_axis(1)) == 1
        self.attack = self.gamepad.get_button(3)
        self.shoot = self.gamepad.get_button(2)

    def _handle_keyboard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.up = True
                if event.key == pygame.K_DOWN:
                    self.down = True
                if event.key == pygame.K_LEFT:
                    self.left = True
                if event.key == pygame.K_RIGHT:
                    self.right = True
                if not self.attack_locked and event.key == pygame.K_SPACE:
                    self.attack = True
                    self.attack_locked = True
                if not self.shoot_locked and event.key == pygame.K_x:
                    self.shoot = True
                    self.shoot_locked = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.up = False
                if event.key == pygame.K_DOWN:
                    self.down = False
                if event.key == pygame.K_LEFT:
                    self.left = False
                if event.key == pygame.K_RIGHT:
                    self.right = False
                if event.key == pygame.K_SPACE:
                    self.attack = False
                    self.attack_locked = False
                if event.key == pygame.K_x:
                    self.shoot = False
                    self.shoot_locked = False
