import math
import pygame
from src.settings import *
import random

class AttackPattern:
    """Base class for attack patterns"""
    def __init__(self, config, all_sprites, bullet_group):
        self.cooldown = config.get('cooldown', 1.0)
        self.last_attack_time = 0
        self.all_sprites = all_sprites
        self.bullet_group = bullet_group
        
    def update(self, dt, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.cooldown * 1000:
            if self.should_attack(enemy, player):
                self.execute_attack(enemy, player)
                self.last_attack_time = current_time
                
    def should_attack(self, enemy, player):
        """Override this to add conditions for when to attack"""
        return True
        
    def execute_attack(self, enemy, player):
        """Override this to implement the actual attack"""
        pass

class NoAttack(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        
    def execute_attack(self, enemy, player):
        pass  # Do nothing

class SingleShotPlayer(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 300)
        
    def execute_attack(self, enemy, player):
        # Calculate direction to player
        direction = player.pos - enemy.pos
        if direction.magnitude() > 0:
            direction = direction.normalize()
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SingleShotDown(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 300)
        
    def execute_attack(self, enemy, player):
        direction = pygame.math.Vector2(0, 1)  # Straight down
        EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SpreadShot(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 300)
        self.bullet_count = config.get('bullet_count', 3)
        self.spread_angle = config.get('spread_angle', 15)  # degrees
        
    def execute_attack(self, enemy, player):
        # Calculate base direction (towards player or straight down)
        if hasattr(self, 'target_player') and getattr(self, 'target_player', True):
            base_direction = player.pos - enemy.pos
            if base_direction.magnitude() > 0:
                base_direction = base_direction.normalize()
        else:
            base_direction = pygame.math.Vector2(0, 1)
            
        # Create spread of bullets
        for i in range(self.bullet_count):
            if self.bullet_count == 1:
                angle = 0
            else:
                angle = -self.spread_angle + (2 * self.spread_angle * i / (self.bullet_count - 1))
            
            # Rotate base direction by angle
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            rotated_dir = pygame.math.Vector2(
                base_direction.x * cos_a - base_direction.y * sin_a,
                base_direction.x * sin_a + base_direction.y * cos_a
            )
            
            EnemyBullet(enemy.rect.center, rotated_dir * self.bullet_speed, [self.all_sprites, self.bullet_group])

class CircularShot(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 250)
        self.bullet_count = config.get('bullet_count', 8)
        
    def execute_attack(self, enemy, player):
        angle_step = 2 * math.pi / self.bullet_count
        
        for i in range(self.bullet_count):
            angle = i * angle_step
            direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class BurstFire(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 350)
        self.burst_count = config.get('burst_count', 3)
        self.burst_delay = config.get('burst_delay', 0.1)  # seconds between shots in burst
        self.current_burst = 0
        self.burst_timer = 0
        self.in_burst = False
        
    def update(self, dt, enemy, player):
        if self.in_burst:
            self.burst_timer += dt
            if self.burst_timer >= self.burst_delay:
                self.execute_single_shot(enemy, player)
                self.current_burst += 1
                self.burst_timer = 0
                
                if self.current_burst >= self.burst_count:
                    self.in_burst = False
                    self.current_burst = 0
                    self.last_attack_time = pygame.time.get_ticks()
        else:
            # Normal cooldown logic
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.cooldown * 1000:
                if self.should_attack(enemy, player):
                    self.in_burst = True
                    self.burst_timer = 0
                    
    def execute_single_shot(self, enemy, player):
        direction = player.pos - enemy.pos
        if direction.magnitude() > 0:
            direction = direction.normalize()
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SpreadShotImage(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 300)
        self.bullet_count = config.get('bullet_count', 3)
        self.spread_angle = config.get('spread_angle', 15)
        self.image_key = config.get('image', 'jesus')

    def execute_attack(self, enemy, player):
        base_direction = player.pos - enemy.pos
        if base_direction.magnitude() > 0:
            base_direction = base_direction.normalize()

        for i in range(self.bullet_count):
            if self.bullet_count == 1:
                angle = 0
            else:
                angle = -self.spread_angle + (2 * self.spread_angle * i / (self.bullet_count - 1))
            
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            rotated_dir = pygame.math.Vector2(
                base_direction.x * cos_a - base_direction.y * sin_a,
                base_direction.x * sin_a + base_direction.y * cos_a
            )
            
            EnemyBullet(enemy.rect.center, rotated_dir * self.bullet_speed, [self.all_sprites, self.bullet_group], image_key=self.image_key, asset_manager=enemy.asset_manager)

class FastForwardShotImage(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.bullet_speed = config.get('bullet_speed', 500)
        self.image_key = config.get('image', 'tang')

    def execute_attack(self, enemy, player):
        direction = pygame.math.Vector2(0, 1)
        EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group], image_key=self.image_key, asset_manager=enemy.asset_manager)

class BlueScreenAttack(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group):
        super().__init__(config, all_sprites, bullet_group)
        self.num_points = config.get('num_points', 5)
        self.delay = config.get('delay', 1.0) # 1 second
        self.points = []

    def execute_attack(self, enemy, player):
        for _ in range(self.num_points):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            point = WarningPoint((x,y), self.delay, [self.all_sprites], enemy.asset_manager)
            self.points.append(point)

class WarningPoint(pygame.sprite.Sprite):
    def __init__(self, pos, delay, groups, asset_manager):
        super().__init__(groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0)) # Yellow point
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.delay = delay * 1000
        self.asset_manager = asset_manager

    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time > self.delay:
            self.image = self.asset_manager.get_image('bsod')
            self.rect = self.image.get_rect(center=self.rect.center)
            # Make it a bullet so it can damage the player
            self.add(self.groups()[0]) # Re-add to update groups if needed
            self.kill() # Or handle collision logic


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, groups, image_key=None, asset_manager=None):
        super().__init__(groups)
        
        if image_key and asset_manager:
            self.image = asset_manager.get_image(image_key)
        else:
            self.image = pygame.Surface((6, 6))
            self.image.fill((255, 100, 100))  # Red enemy bullet
        
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = velocity
        
    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Remove when off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

def create_attack_pattern(config, all_sprites, bullet_group):
    """Factory function to create attack patterns"""
    pattern_type = config.get('type', 'none')
    
    if pattern_type == 'none':
        return NoAttack(config, all_sprites, bullet_group)
    elif pattern_type == 'single_shot_player':
        return SingleShotPlayer(config, all_sprites, bullet_group)
    elif pattern_type == 'single_shot_down':
        return SingleShotDown(config, all_sprites, bullet_group)
    elif pattern_type == 'spread_shot':
        return SpreadShot(config, all_sprites, bullet_group)
    elif pattern_type == 'circular_shot':
        return CircularShot(config, all_sprites, bullet_group)
    elif pattern_type == 'burst_fire':
        return BurstFire(config, all_sprites, bullet_group)
    elif pattern_type == 'spread_shot_image':
        return SpreadShotImage(config, all_sprites, bullet_group)
    elif pattern_type == 'fast_forward_shot_image':
        return FastForwardShotImage(config, all_sprites, bullet_group)
    elif pattern_type == 'blue_screen_attack':
        return BlueScreenAttack(config, all_sprites, bullet_group)
    else:
        return NoAttack(config, all_sprites, bullet_group)