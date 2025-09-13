import pygame

class Coin(pygame.sprite.Sprite):
    coin_positions = [
        (350, 700, 20, 20),
        (640, 675, 20, 20),
        (620, 620, 20, 20),
        (600, 620, 20, 20),
        (630, 620, 20, 20),
        (640, 620, 20, 20),
        (580, 625, 20, 20),
        (550, 600, 20, 20),
        (450, 600, 20, 20)
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((255, 215, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))