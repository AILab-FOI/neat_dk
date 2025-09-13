import pygame

class Punishment(pygame.sprite.Sprite):
    punishment_positions = [
        (25, 650, 20, 100),
        (20, 650, 20, 100),
        (15, 650, 20, 100),
        (10, 650, 20, 100),
        (480, 655, 48, 22),
        (433, 650, 48, 22),
        (386, 646, 48, 22),
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((255, 215, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))