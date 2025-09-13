import pygame
from projekt.config import *

class Ladder(pygame.sprite.Sprite):
    ladder_positions = [
        (553, 650, 25, 80),
        (290, 535, 25, 110),
        (98, 550, 25, 80),
        (338, 440, 25, 100) ,
        (553, 450, 25, 80),
        (220, 350, 25, 100),
        (98, 355, 25, 80),
        (553, 253, 25, 80),
        (385, 160, 25, 90),
        (243, 80, 25, 180),
        (195, 80, 25, 180),

    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_position(self):
        return [self.rect.x, self.rect.y]