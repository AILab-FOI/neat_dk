import pygame

class SuperCoin(pygame.sprite.Sprite):
    scoin_positions = [
        #(630, 660, 20, 20)
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))