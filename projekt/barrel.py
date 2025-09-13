import pygame
from projekt.config import *
import os

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms, borders):
        super().__init__()

        self.x = x
        self.y = y

        self.width = BARREL_WIDTH
        self.height = BARREL_HEIGHT

        self.vel_x = BARREL_SPEED
        self.vel_y = 0

        self.platforms = platforms
        self.borders = borders

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((88, 57, 39))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.animations = {
            'right': [
                self.load_scaled_image('barrel1.png', self.width, self.height),
                self.load_scaled_image('barrel2.png', self.width, self.height),
                self.load_scaled_image('barrel3.png', self.width, self.height),
                self.load_scaled_image('barrel4.png', self.width, self.height)
            ],
            'left': [
                self.load_scaled_image('barrel4.png', self.width, self.height),
                self.load_scaled_image('barrel3.png', self.width, self.height),
                self.load_scaled_image('barrel2.png', self.width, self.height),
                self.load_scaled_image('barrel1.png', self.width, self.height)
            ],
        }

        self.direction = 'right'
        self.image_index = 0
        self.animation_counter = 0
        self.image = self.animations[self.direction][self.image_index]

    def update_animation(self):
        if self.vel_x > 0:
            seq = self.animations[self.direction]
            self.animation_counter += 1
            if self.animation_counter >= 5:
                self.animation_counter = 0
                self.image_index = (self.image_index + 1) % len(seq)
            self.image = seq[self.image_index]

        else:
            seq = self.animations[self.direction]
            self.animation_counter += 1
            if self.animation_counter >= 5:
                self.animation_counter = 0
                self.image_index = (self.image_index + 1) % len(seq)
            self.image = seq[self.image_index]


    def load_scaled_image(self, filename, width, height):
        path = os.path.join('projekt', 'Assets', filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))


    def move_barrel(self):
        prev_y = self.y
        prev_x = self.x

        self.x += self.vel_x

        self.vel_y += GRAVITY
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y

        self.update_animation()
        return prev_y, prev_x

    def check_collision_border(self, prev_x):
        for border in self.borders:
            if self.rect.colliderect(border.rect):
                if border.rect.width < border.rect.height:
                    if prev_x + self.width <= border.rect.left:
                        self.x = border.rect.left - self.width
                        self.vel_x = -self.vel_x
                    elif prev_x >= border.rect.right:
                        self.x = border.rect.right
                        self.vel_x = -self.vel_x
                    self.rect.x = self.x

    def platform_collision(self):
        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.y + self.height <= platform.rect.top + 10 and self.vel_y >= 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.rect.y = self.y

    def update_barrel(self):
        prev_y, prev_x = self.move_barrel()
        self.check_collision_border(prev_x)
        self.platform_collision()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_state(self):
        return [self.rect.x, self.rect.y, self.vel_x, self.vel_y]
