import pygame
import json
import os
from src.movement_patterns import create_movement_pattern
from src.attack_patterns import create_attack_pattern

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type, asset_manager, player, groups):
        super().__init__(groups)
        
        # Load enemy configuration
        self.config = self.load_enemy_config(enemy_type)
        
        # Core attributes from config
        self.health = self.config['health']
        self.max_health = self.health
        self.enemy_type = enemy_type
        
        # Load sprite
        asset_key = self.config.get('asset_key', 'enemy')
        self.image = asset_manager.get_image(asset_key)
        if not self.image:
            # Fallback to basic enemy sprite
            self.image = asset_manager.get_image('enemy')
        self.rect = self.image.get_rect(center=pos)
        
        # Position vector for smooth movement
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # References to other game objects
        self.player = player
        self.asset_manager = asset_manager
        
        # Get sprite groups for attack patterns
        all_sprites = groups[0] if groups else None
        enemy_bullet_group = None
        
        # Try to get the bullet group from the game state
        # This is a bit hacky but works for our current structure
        for group in groups:
            if hasattr(group, '_spritedict'):
                # Check if this group contains bullets by looking for EnemyBullet instances
                for sprite in group:
                    if hasattr(sprite, '__class__') and 'Bullet' in sprite.__class__.__name__:
                        enemy_bullet_group = group
                        break
        
        # If we couldn't find a bullet group, create a temporary one
        if enemy_bullet_group is None:
            enemy_bullet_group = pygame.sprite.Group()
        
        # Behavior components created via factories based on config
        self.movement = create_movement_pattern(self.config['movement'])
        self.attack = create_attack_pattern(self.config['attack'], all_sprites, enemy_bullet_group)
        
        # Internal state
        self.age = 0.0  # Time since spawn
        
    def load_enemy_config(self, enemy_type):
        """Load enemy configuration from JSON file"""
        config_path = os.path.join('data', 'enemy_config.json')
        try:
            with open(config_path, 'r') as f:
                configs = json.load(f)
                return configs.get(enemy_type, configs.get('basic', self.get_default_config()))
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()
            
    def get_default_config(self):
        """Default enemy configuration"""
        return {
            'health': 20,
            'asset_key': 'enemy',
            'movement': {
                'type': 'straight',
                'speed': 100
            },
            'attack': {
                'type': 'none'
            }
        }
        
    def update(self, dt):
        """Update enemy state"""
        self.age += dt
        
        # Delegate behavior to components
        self.movement.update(dt, self)
        if self.player:
            self.attack.update(dt, self, self.player)
        
        # Update rect from position vector
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Basic despawn logic - remove when off screen
        screen_rect = pygame.display.get_surface().get_rect()
        expanded_rect = screen_rect.inflate(100, 100)  # Give some margin
        if not self.rect.colliderect(expanded_rect):
            self.kill()
            
    def take_damage(self, damage=5):
        """Take damage and return True if enemy is destroyed"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False
        
    def get_score_value(self):
        """Get the score value for destroying this enemy"""
        score_values = {
            'scout': 50,
            'fighter': 100,
            'gunship': 150,
            'interceptor': 120,
            'bomber': 200,
            'basic': 75
        }
        return score_values.get(self.enemy_type, 50)