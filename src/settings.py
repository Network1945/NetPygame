# Game constants and settings
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SPEED = 300
PLAYER_SHOOT_DELAY = 200  # milliseconds

# Bullet settings
BULLET_SPEED = 500

# Enemy settings
ENEMY_SPEED = 150

# Game settings
SCORE_FONT_SIZE = 24

# --- 네트워크 스폰 설정 추가 ---
# Pygame 커스텀 이벤트 정의
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1

# 패킷 타입과 적 종류 매핑
PACKET_TO_ENEMY_MAP = {
    'tcp': 'interceptor',       # TCP -> 인터셉터 (빠른 적)
    'icmp': 'fighter',  # ICMP -> 파이터
    'arp': 'scout',         # ARP -> 스카우트 (지그재그 움직임)
    'udp': 'gunship',       # UDP -> 건쉽 (체력이 높은 적)
}

# 네트워크 스폰 쿨다운 (초)
NETWORK_SPAWN_COOLDOWN = 1.0