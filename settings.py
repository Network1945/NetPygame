# Game settings and constants
import pygame

# Custom Events for Network Integration
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1

# Mapping packet types to enemy types
PACKET_TO_ENEMY_MAP = {
    'tcp': 'basic',
    'icmp': 'fast', 
    'arp': 'zigzag',
    'udp': 'tank'
}

# Screen dimensions
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_BOUNDARY = 20  # pixels from screen edge

# Bullet settings
BULLET_SPEED = 7
BULLET_WIDTH = 5
BULLET_HEIGHT = 10

# Enemy settings
ENEMY_SPEED = 3
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 30
ENEMY_SPAWN_RATE = 1000  # milliseconds

# Enemy type colors and properties
ENEMY_COLORS = {
    'basic': RED,
    'fast': (255, 100, 100),    # Light red
    'zigzag': (255, 0, 255),    # Magenta
    'tank': (139, 69, 19),      # Brown
}

# Enemy type speeds
ENEMY_SPEEDS = {
    'basic': 2,
    'fast': 5,
    'zigzag': 1,
    'tank': 1,
}

# Enemy point values
ENEMY_POINTS = {
    'basic': 10,
    'fast': 20,
    'zigzag': 30,
    'tank': 50,
}

# Game settings
PLAYER_LIVES = 3

# Network Monitor settings
NETWORK_SPAWN_COOLDOWN = 0.1  # seconds between network-triggered spawns per type
NETWORK_MONITOR_ENABLED = True