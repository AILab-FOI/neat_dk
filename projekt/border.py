import pygame
from projekt.config import *

class Border(pygame.sprite.Sprite):
    border_positions = [
        (0, 0, 675, 1),
        (0, 770, 675, 1),
        (0, 0, 1, 770),
        (675, 0, 1, 770)
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
