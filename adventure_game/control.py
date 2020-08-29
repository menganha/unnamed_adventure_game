import pygame


class Control():
    def __init__(self):
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.action = False
        self.previous_frame_action = False
        self.exit = False
        pygame.joystick.init()
        self.has_gamepad = pygame.joystick.get_count()
        if self.has_gamepad:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
        else:
            pygame.joystick.quit()

    def handle_input(self):
        self.previous_frame_action = self.action
        if self.has_gamepad:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
            self.moving_right = round(self.gamepad.get_axis(0)) == 1
            self.moving_left = round(self.gamepad.get_axis(0)) == -1
            self.moving_up = round(self.gamepad.get_axis(1)) == -1
            self.moving_down = round(self.gamepad.get_axis(1)) == 1
            self.action = self.gamepad.get_button(3)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.moving_up = True
                    if event.key == pygame.K_DOWN:
                        self.moving_down = True
                    if event.key == pygame.K_LEFT:
                        self.moving_left = True
                    if event.key == pygame.K_RIGHT:
                        self.moving_right = True
                    if event.key == pygame.K_SPACE:
                        self.action = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.moving_up = False
                    if event.key == pygame.K_DOWN:
                        self.moving_down = False
                    if event.key == pygame.K_LEFT:
                        self.moving_left = False
                    if event.key == pygame.K_RIGHT:
                        self.moving_right = False
                    if event.key == pygame.K_SPACE:
                        self.action = False
