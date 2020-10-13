import pygame
from adventure_game.config import DIS_WIDTH, DIS_HEIGHT, BLACK


class Text:
    def __init__(
        self,
        font: pygame.font.Font,
        text="",
        color=BLACK,
        background=None,
        alpha=255,
        tX=0,
        tY=0,
    ):
        self.font = font
        self.text = text
        self.color = color
        self.background = background
        self.tX = tX
        self.tY = tY
        self.textS = self.font.render(self.text, False, color, background)
        self.tW, self.tH = self.textS.get_size()
        self.alpha = alpha
        self.alpha_change = 1

    def center(self, offX=0, offY=0):
        self.tX, self.tY = self.get_coordinates_to_center(self.tW, self.tH, DIS_WIDTH, DIS_HEIGHT)
        self.tX += offX
        self.tY += offY

    def reRender(self, color=None, background=None):
        if not color:
            color = self.color
        if not background:
            background = self.background
        self.textS = self.font.render(self.text, False, color, background)
        self.textS.set_alpha(self.alpha)

    def isMousein(self, mx, my):
        textR = self.textS.get_rect(x=self.tX, y=self.tY)
        return textR.collidepoint(mx, my)

    def update_alpha(self, alpha=None):
        if alpha:
            self.alpha = alpha
        else:
            if self.alpha >= 255 - self.alpha_change:
                self.alpha_change = -abs(self.alpha_change)
            elif self.alpha <= self.alpha_change:
                self.alpha_change = abs(self.alpha_change)
            self.alpha += self.alpha_change

        self.textS.convert_alpha()
        self.textS.set_alpha(self.alpha)

    def draw(self, display: pygame.Surface):
        display.blit(self.textS, [self.tX, self.tY])

    @staticmethod
    def get_coordinates_to_center(objWidth, objHeight, disWidth, disHeight):
        centerX = round(disWidth / 2 - objWidth / 2)
        centerY = round(disHeight / 2 - objHeight / 2)
        return centerX, centerY
