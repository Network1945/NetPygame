import pygame
import os

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        
    def load_images(self):
        """Load all game images"""
        image_path = os.path.join('assets', 'images')
        
        # Create placeholder images if actual assets don't exist
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            
        # Load or create placeholder images
        try:
            if os.path.exists(os.path.join(image_path, 'player.png')):
                self.images['player'] = pygame.image.load(os.path.join(image_path, 'player.png')).convert_alpha()
            else:
                raise FileNotFoundError()
        except (pygame.error, FileNotFoundError):
            # Create placeholder player sprite
            player_surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            pygame.draw.polygon(player_surf, (0, 255, 0), [(16, 0), (0, 48), (32, 48)])
            self.images['player'] = player_surf
            
        try:
            if os.path.exists(os.path.join(image_path, 'bullet.png')):
                self.images['bullet'] = pygame.image.load(os.path.join(image_path, 'bullet.png')).convert_alpha()
            else:
                raise FileNotFoundError()
        except (pygame.error, FileNotFoundError):
            # Create placeholder bullet sprite
            bullet_surf = pygame.Surface((4, 12), pygame.SRCALPHA)
            bullet_surf.fill((255, 255, 0))
            self.images['bullet'] = bullet_surf
            
        # Load basic enemy sprite
        try:
            if os.path.exists(os.path.join(image_path, 'enemy.png')):
                self.images['enemy'] = pygame.image.load(os.path.join(image_path, 'enemy.png')).convert_alpha()
            else:
                raise FileNotFoundError()
        except (pygame.error, FileNotFoundError):
            # Create placeholder enemy sprite
            enemy_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(enemy_surf, (255, 0, 0), (12, 12), 12)
            self.images['enemy'] = enemy_surf
            
        # Load different enemy types with placeholder sprites
        enemy_types = {
            'enemy_scout': (20, 20, (255, 165, 0)),      # Orange triangle
            'enemy_fighter': (28, 28, (255, 100, 100)),   # Red diamond
            'enemy_gunship': (32, 24, (128, 128, 255)),   # Blue rectangle
            'enemy_interceptor': (24, 16, (255, 255, 100)), # Yellow oval
            'enemy_bomber': (36, 32, (128, 255, 128))     # Green hexagon
        }
        
        for enemy_key, (width, height, color) in enemy_types.items():
            try:
                if os.path.exists(os.path.join(image_path, f'{enemy_key}.png')):
                    img = pygame.image.load(os.path.join(image_path, f'{enemy_key}.png')).convert_alpha()
                    # Scale down the image (e.g., to half size)
                    scale_factor = 0.1
                    new_size = (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                    img = pygame.transform.smoothscale(img, new_size)
                    self.images[enemy_key] = img
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                # Create placeholder sprite based on enemy type
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                
                if 'scout' in enemy_key:
                    # Triangle
                    points = [(width//2, 0), (0, height), (width, height)]
                    pygame.draw.polygon(surf, color, points)
                elif 'fighter' in enemy_key:
                    # Diamond
                    points = [(width//2, 0), (width, height//2), (width//2, height), (0, height//2)]
                    pygame.draw.polygon(surf, color, points)
                elif 'gunship' in enemy_key:
                    # Rectangle
                    pygame.draw.rect(surf, color, (0, 0, width, height))
                elif 'interceptor' in enemy_key:
                    # Oval
                    pygame.draw.ellipse(surf, color, (0, 0, width, height))
                elif 'bomber' in enemy_key:
                    # Hexagon
                    points = [(width//4, 0), (3*width//4, 0), (width, height//2), 
                             (3*width//4, height), (width//4, height), (0, height//2)]
                    pygame.draw.polygon(surf, color, points)
                else:
                    # Default circle
                    pygame.draw.circle(surf, color, (width//2, height//2), min(width, height)//2)
                
                self.images[enemy_key] = surf
        
        # Load boss images
        try:
            if os.path.exists(os.path.join(image_path, 'migamboss.png')):
                img = pygame.image.load(os.path.join(image_path, 'migamboss.png')).convert_alpha()
                # Scale boss image appropriately (larger than enemies but not too big)
                scale_factor = 0.3
                new_size = (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                img = pygame.transform.smoothscale(img, new_size)
                self.images['migamboss'] = img
            else:
                # Create placeholder boss sprite if image not found
                boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(boss_surf, (255, 0, 255), (30, 30), 30)  # Magenta boss
                self.images['migamboss'] = boss_surf
        except (pygame.error, FileNotFoundError):
            # Create placeholder boss sprite
            boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(boss_surf, (255, 0, 255), (30, 30), 30)  # Magenta boss
            self.images['migamboss'] = boss_surf
            
        # Load custom boss attack images
        custom_images = {
            'jesus': (100, 100, (255, 255, 255)),
            'tang': (50, 50, (255, 100, 100)),
            'bsod': (100, 100, (0, 0, 255))
        }

        scale_targets = {"jesus","bsod"}
        scale_factor = 0.4

        for key, (width, height, color) in custom_images.items():
            try:
                img_path = os.path.join(image_path, f"{key}.png")
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    if key == "jesus":
                        w, h = img.get_size()
                        new_size = (int(w * 0.4), int(h * scale_factor))
                        img = pygame.transform.scale(img, new_size)
                    elif key == "tang":
                        w, h = img.get_size()
                        new_size = (int(w * 0.3), int(h * scale_factor))
                        img = pygame.transform.scale(img, new_size)
                    elif key == "bsod":
                        w, h = img.get_size()
                        new_size = (int(w * 0.3), int(h * scale_factor))
                        img = pygame.transform.scale(img, new_size)
                    
                    else:
                        w, h = img.get_size()
                        new_size = (int(w * 1.0), int(h * scale_factor))
                        img = pygame.transform.scale(img, new_size)
                    self.images[key] = img
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                surf.fill(color)
                self.images[key] = surf

        # Load powerup images
        powerup_images = {
            'shield': (32, 32, (0, 191, 255)),       # Deep Sky Blue circle
            'rapid_fire': (32, 32, (255, 215, 0)),  # Gold lightning bolt
            'spread_shot': (32, 32, (148, 0, 211)), # Dark Violet three dots
        }

        for key, (width, height, color) in powerup_images.items():
            try:
                img_path = os.path.join(image_path, f"{key}.png")
                if os.path.exists(img_path):
                    self.images[key] = pygame.image.load(img_path).convert_alpha()
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                if key == 'shield':
                    pygame.draw.circle(surf, color, (width//2, height//2), width//2, 3)
                elif key == 'rapid_fire':
                    pygame.draw.polygon(surf, color, [(16, 2), (8, 16), (14, 16), (6, 30), (24, 14), (18, 14)])
                elif key == 'spread_shot':
                    pygame.draw.circle(surf, color, (width//2, 8), 4)
                    pygame.draw.circle(surf, color, (8, 24), 4)
                    pygame.draw.circle(surf, color, (width - 8, 24), 4)
                self.images[key] = surf

    def load_sounds(self):
        """Load all game sounds"""
        sound_path = os.path.join('assets', 'sounds')
        
        if not os.path.exists(sound_path):
            os.makedirs(sound_path)
            
        # Create placeholder sounds or load real ones
        try:
            if os.path.exists(os.path.join(sound_path, 'shoot.wav')):
                self.sounds['shoot'] = pygame.mixer.Sound(os.path.join(sound_path, 'shoot.wav'))
            else:
                self.sounds['shoot'] = None
        except pygame.error:
            # Create a simple beep sound as placeholder
            self.sounds['shoot'] = None
            
        try:
            if os.path.exists(os.path.join(sound_path, 'explosion.wav')):
                self.sounds['explosion'] = pygame.mixer.Sound(os.path.join(sound_path, 'explosion.wav'))
            else:
                self.sounds['explosion'] = None
        except pygame.error:
            self.sounds['explosion'] = None
            
    def load_fonts(self):
        """Load game fonts"""
        font_path = os.path.join('assets', 'fonts')
        
        if not os.path.exists(font_path):
            os.makedirs(font_path)
            
        # Use default font if custom font not available
        self.fonts['score'] = pygame.font.Font(None, 24)
        self.fonts['title'] = pygame.font.Font(None, 48)
        
    def load_all(self):
        """Load all assets"""
        self.load_images()
        self.load_sounds()
        self.load_fonts()
        
    def get_image(self, key):
        """Get image by key"""
        return self.images.get(key)
        
    def get_sound(self, key):
        """Get sound by key"""
        return self.sounds.get(key)
        
    def get_font(self, key):
        """Get font by key"""
        return self.fonts.get(key)
        
    def play_sound(self, key):
        """Play sound by key"""
        sound = self.sounds.get(key)
        if sound:
            sound.play()