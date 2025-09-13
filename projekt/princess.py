import pygame
from projekt.config import *
import os

class Princess(pygame.sprite.Sprite):

    def __init__(self, x, y, player):
        super().__init__()

        self.x = x
        self.y = y
        self.player = player

        self.width = PRINCESS_WIDTH
        self.height = PRINCESS_HEIGHT

        self.image = py.image.load(os.path.join('projekt', 'Assets', 'peach.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 40))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))


    def draw(self, screen):
        screen.blit(self.image, self.rect)