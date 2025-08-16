import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - PLAYER_BOUNDARY
        self.speedx = 0
        self.speedy = 0

    def update(self):
        # Movement logic based on key presses (8-directional)
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        
        # Horizontal movement
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = PLAYER_SPEED
            
        # Vertical movement
        if keystate[pygame.K_UP] or keystate[pygame.K_w]:
            self.speedy = -PLAYER_SPEED
        if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
            self.speedy = PLAYER_SPEED
        
        # Apply movement
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Keep player within boundaries
        if self.rect.right > WIDTH - PLAYER_BOUNDARY:
            self.rect.right = WIDTH - PLAYER_BOUNDARY
        if self.rect.left < PLAYER_BOUNDARY:
            self.rect.left = PLAYER_BOUNDARY
        if self.rect.top < PLAYER_BOUNDARY:
            self.rect.top = PLAYER_BOUNDARY
        if self.rect.bottom > HEIGHT - PLAYER_BOUNDARY:
            self.rect.bottom = HEIGHT - PLAYER_BOUNDARY

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speedy
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type='basic'):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLORS[enemy_type])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = ENEMY_SPEEDS[enemy_type]
        self.speedx = 0
        
        # Type-specific initialization
        if enemy_type == 'zigzag':
            self.speedx = random.choice([-2, 2])
        elif enemy_type == 'tank':
            self.image = pygame.Surface((ENEMY_WIDTH + 20, ENEMY_HEIGHT + 10))
            self.image.fill(ENEMY_COLORS[enemy_type])
            self.rect = self.image.get_rect()
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

    def update(self):
        if self.enemy_type == 'basic':
            self.rect.y += self.speedy
            
        elif self.enemy_type == 'fast':
            self.rect.y += self.speedy
            
        elif self.enemy_type == 'zigzag':
            self.rect.y += self.speedy
            self.rect.x += self.speedx
            # Bounce off screen edges
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.speedx = -self.speedx
                
        elif self.enemy_type == 'tank':
            self.rect.y += self.speedy
        
        # Remove enemy if it goes off screen
        if self.rect.top > HEIGHT:
            self.kill()