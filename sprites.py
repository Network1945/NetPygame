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
        
        # Health system attributes
        self.max_health = PLAYER_MAX_HEALTH
        self.current_health = self.max_health
        self.invincible = False
        self.invincibility_start_time = 0
        self.last_damage_time = 0
        self.last_regen_time = pygame.time.get_ticks()

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
        
        # Update invincibility status
        if self.invincible:
            if pygame.time.get_ticks() - self.invincibility_start_time > PLAYER_INVINCIBILITY_DURATION:
                self.invincible = False
        
        # Health regeneration logic
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > PLAYER_REGEN_COOLDOWN:
            if now - self.last_regen_time > (1000 / PLAYER_REGEN_RATE_PER_SECOND):
                if self.current_health < self.max_health:
                    self.current_health = min(self.max_health, self.current_health + PLAYER_REGEN_AMOUNT)
                    self.last_regen_time = now

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet
    
    def take_damage(self, amount):
        if not self.invincible:
            self.current_health -= amount
            self.last_damage_time = pygame.time.get_ticks()
            self.invincible = True
            self.invincibility_start_time = pygame.time.get_ticks()
            if self.current_health < 0:
                self.current_health = 0

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
        
        # Assign damage based on enemy type
        self.damage = ENEMY_DAMAGE[enemy_type]
        
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