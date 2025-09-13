import pygame
from projekt.config import *

class LadderDetect(pygame.sprite.Sprite):
    ladder_detect_positions = [
        # 1 1 (553, 650, 25, 80)
        (553, 630, 25, 25),  # gore
        (528, 725, 75, 25),  # dolje

        # 2 velika (290, 545, 25, 100)
        (290, 525, 25, 25),  # gore
        (265, 635, 75, 25),  # dolje

        # 2 mala (98, 550, 25, 80)
        (98, 530, 25, 25),  # gore
        (73, 625, 75, 25),  # dolje

        # 3 velika (338, 440, 25, 100)
        (338, 420, 25, 25),  # gore
        (313, 535, 75, 25),  # dolje

        # 3 mala (553, 450, 25, 80)
        (553, 430, 25, 25),  # gore
        (528, 525, 75, 25),  # dolje

        # 4 velika (220, 340, 25, 100)
        (220, 320, 25, 25),  # gore
        (220, 435, 75, 25),  # dolje

        # 4 mala (98, 355, 25, 80)
        (98, 335, 25, 25),  # gore
        (98, 425, 75, 25),  # dolje

        # 5 1 (553, 253, 25, 80)
        (553, 233, 25, 25),  # gore
        (528, 328, 75, 25),  # dolje

        # 6 1 (385, 160, 25, 90)
        (385, 140, 25, 25),  # gore
        (360, 248, 75, 25),  # dolje

        # 6 desna velika (243, 80, 25, 180)
        (243, 60, 25, 25),  # gore
        (218, 248, 75, 25),  # dolje

        # 6 lijeva velika (195, 80, 25, 180)
        (195, 60, 25, 25),  # gore
        (170, 248, 75, 25),  # dolje
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
