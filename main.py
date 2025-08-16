import pygame
import random
import sys
from settings import *
from sprites import Player, Enemy, Bullet
from network import NetworkMonitor

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: Audio not available, continuing without sound")

# Create screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Striker-1945")
clock = pygame.time.Clock()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game variables
score = 0
lives = PLAYER_LIVES
font = pygame.font.Font(None, 36)

# Enemy spawn timer
last_enemy_spawn = 0

# Initialize and start network monitor
network_monitor = None
if NETWORK_MONITOR_ENABLED:
    network_monitor = NetworkMonitor()
    network_monitor.start()

# Game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = player.shoot()
                all_sprites.add(bullet)
                bullets.add(bullet)
        elif event.type == ENEMY_SPAWN_EVENT:
            # Handle network-triggered enemy spawn
            enemy_type = event.enemy_type
            packet_type = event.packet_type
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)
    
    # Update
    all_sprites.update()
    
    # Spawn enemies (timer-based, only if network monitoring is disabled)
    if not NETWORK_MONITOR_ENABLED:
        now = pygame.time.get_ticks()
        if now - last_enemy_spawn > ENEMY_SPAWN_RATE:
            last_enemy_spawn = now
            # Randomly choose enemy type with different probabilities
            enemy_types = ['basic', 'basic', 'fast', 'zigzag', 'tank']  # basic is more common
            enemy_type = random.choice(enemy_types)
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)
    
    # Check for collisions - bullets hit enemies
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += ENEMY_POINTS[hit.enemy_type]
    
    # Check for collisions - player hit by enemy
    hits = pygame.sprite.spritecollide(player, enemies, True)
    if hits:
        lives -= 1
        if lives <= 0:
            running = False
    
    # Draw / render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Draw HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    
    # Show network monitor status
    if network_monitor:
        net_status = font.render("Network: ON", True, GREEN)
        screen.blit(net_status, (10, 90))
        
        # Show packet counts (smaller font)
        small_font = pygame.font.Font(None, 24)
        stats = network_monitor.get_stats()
        y_offset = 120
        for packet_type, count in stats.items():
            stat_text = small_font.render(f"{packet_type.upper()}: {count}", True, WHITE)
            screen.blit(stat_text, (10, y_offset))
            y_offset += 25
    else:
        net_status = font.render("Network: OFF", True, RED)
        screen.blit(net_status, (10, 90))
    
    # After drawing everything, flip the display
    pygame.display.flip()

# Graceful shutdown
print("🎮 Game shutting down...")
if network_monitor:
    print("🌐 Stopping network monitor...")
    network_monitor.stop()
    network_monitor.join(timeout=2)  # Wait up to 2 seconds
    print("✅ Network monitor stopped")

pygame.quit()
sys.exit()