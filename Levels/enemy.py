import pygame


class Enemy:
    def __init__(self, x, y, min_x, max_x, speed=2):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction

        if self.rect.x <= self.min_x:
            self.direction = 1
        if self.rect.x >= self.max_x:
            self.direction = -1

    def draw(self, screen, kamera_x):
        pygame.draw.rect(screen, (200, 50, 50), self.rect.move(-kamera_x, 0))
