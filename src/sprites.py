import pygame
from src.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, asset_manager, screen_rect):
        super().__init__()
        
        # Image and rect
        self.image = asset_manager.get_image('player')
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        
        # Screen boundaries
        self.screen_rect = screen_rect
        
        # Shooting
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.last_shot_time = 0
        self.weapon_level = 1
        
        # Health and lives system
        self.max_health = 100
        self.health = self.max_health
        self.lives = 3
        self.max_lives = 3
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1500  # 1.5 seconds in milliseconds
        self.is_dead = False
        
        # Asset manager reference
        self.asset_manager = asset_manager
        
        # Sprite groups will be set by the game state
        self.all_sprites = None
        self.bullet_group = None
        
    def set_sprite_groups(self, all_sprites, bullet_group):
        """Set sprite groups for bullet spawning"""
        self.all_sprites = all_sprites
        self.bullet_group = bullet_group
        
    def get_input(self):
        """Handle player input"""
        keys = pygame.key.get_pressed()
        
        # Movement input
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        
        # Normalize direction to prevent faster diagonal movement
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
        # Shooting input
        if keys[pygame.K_SPACE]:
            self.shoot()
            
    def shoot(self):
        """Create bullets based on weapon level"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            
            if self.weapon_level == 1:
                # Single bullet from center
                Bullet(self.rect.midtop, self.asset_manager, [self.all_sprites, self.bullet_group])
            elif self.weapon_level == 2:
                # Two bullets from sides
                Bullet((self.rect.left + 8, self.rect.top), self.asset_manager, [self.all_sprites, self.bullet_group])
                Bullet((self.rect.right - 8, self.rect.top), self.asset_manager, [self.all_sprites, self.bullet_group])
            elif self.weapon_level >= 3:
                # Three bullets: center and angled
                Bullet(self.rect.midtop, self.asset_manager, [self.all_sprites, self.bullet_group])
                Bullet((self.rect.left + 8, self.rect.top), self.asset_manager, [self.all_sprites, self.bullet_group], angle=-15)
                Bullet((self.rect.right - 8, self.rect.top), self.asset_manager, [self.all_sprites, self.bullet_group], angle=15)
                
            # Play shoot sound
            self.asset_manager.play_sound('shoot')
            
    def upgrade_weapon(self):
        """Upgrade weapon level"""
        self.weapon_level += 1
        if self.weapon_level > 5:
            self.weapon_level = 5
            
    def take_damage(self, damage=20):
        """Take damage if not invulnerable"""
        if self.invulnerable or self.is_dead:
            return False
            
        self.health -= damage
        
        # Start invulnerability period
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        # Check if player died
        if self.health <= 0:
            self.health = 0
            self.die()
            return True
            
        return False
        
    def die(self):
        """Handle player death"""
        self.lives -= 1
        
        if self.lives <= 0:
            # Game over
            self.is_dead = True
        else:
            # Respawn with full health
            self.respawn()
            
    def respawn(self):
        """Respawn player with full health and invulnerability"""
        self.health = self.max_health
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        # Reset position to bottom center
        self.pos.x = self.screen_rect.centerx
        self.pos.y = self.screen_rect.bottom - 100
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
    def restore_health(self, amount=20):
        """Restore health up to maximum"""
        self.health = min(self.max_health, self.health + amount)
        
    def add_life(self):
        """Add an extra life"""
        if self.lives < self.max_lives:
            self.lives += 1
            
    def keep_in_bounds(self):
        """Keep player within screen boundaries"""
        self.rect.clamp_ip(self.screen_rect)
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery
        
    def update(self, dt):
        """Update player state"""
        # Don't process input if dead
        if not self.is_dead:
            self.get_input()
            
            # Update position
            self.pos += self.direction * self.speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))
            
            # Keep in bounds
            self.keep_in_bounds()
        
        # Update invulnerability
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time > self.invulnerable_duration:
                self.invulnerable = False
                
    def draw(self, screen):
        """Custom draw method to handle invulnerability flashing"""
        if self.invulnerable:
            # Flash every 100ms during invulnerability
            current_time = pygame.time.get_ticks()
            if (current_time // 100) % 2 == 0:
                screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, asset_manager, groups, angle=0):
        super().__init__(groups)
        
        # Image and rect
        self.image = asset_manager.get_image('bullet')
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # Calculate velocity based on angle
        if angle == 0:
            self.velocity = pygame.math.Vector2(0, -BULLET_SPEED)
        else:
            # Convert angle to radians and create angled velocity
            import math
            angle_rad = math.radians(angle)
            self.velocity = pygame.math.Vector2(
                math.sin(angle_rad) * BULLET_SPEED,
                -math.cos(angle_rad) * BULLET_SPEED
            )
            
    def update(self, dt):
        """Update bullet position"""
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Remove bullet when it goes off screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, asset_manager, groups):
        super().__init__(groups)
        
        # Image and rect
        self.image = asset_manager.get_image('enemy')
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, ENEMY_SPEED)
        
        # Health
        self.health = 1
        
    def update(self, dt):
        """Update enemy position"""
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Remove enemy when it goes off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
    def take_damage(self, damage=1):
        """Take damage and die if health reaches 0"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True  # Enemy destroyed
        return False