import pygame
from src.settings import *
from src.sprites import Player
from src.enemy import Enemy
from src.attack_patterns import EnemyBullet
from src.wave_manager import WaveManager
import random

class State:
    """Base state class"""
    def __init__(self, game):
        self.game = game
        
    def handle_events(self, events):
        """Handle events for this state"""
        pass
        
    def update(self, dt):
        """Update state logic"""
        pass
        
    def draw(self, screen):
        """Draw state to screen"""
        pass


class GameplayState(State):
    def __init__(self, game):
        super().__init__(game)
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()  # Player bullets
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()  # Enemy bullets
        
        # Create player
        player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.player = Player(player_pos, game.asset_manager, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player.set_sprite_groups(self.all_sprites, self.bullet_group)
        self.all_sprites.add(self.player)
        self.player_group.add(self.player)
        
        # Game variables
        self.score = 0
        self.game_won = False  # Victory state
        
        # Wave management
        sprite_groups = [self.all_sprites, self.enemy_group, self.enemy_bullet_group]
        self.wave_manager = WaveManager(game.asset_manager, self.player, sprite_groups)
        
    def handle_events(self, events):
        """Handle gameplay events"""
        for event in events:
            # --- 네트워크 스폰 이벤트 처리 추가 ---
            if event.type == ENEMY_SPAWN_EVENT:
                if event.source == 'network':
                    self.spawn_network_enemy(event.enemy_type)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.running = False
                elif event.key == pygame.K_r and (self.player.is_dead or self.game_won):
                    # Restart game from game over or victory screen
                    self.game.state_manager.change_state('gameplay')
    
    # --- 네트워크 적 스폰을 위한 새로운 메서드 추가 ---
    def spawn_network_enemy(self, enemy_type):
        """Spawns an enemy from a network event."""
        # 화면 상단 밖에서 랜덤한 x 위치에 스폰
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(-100, -50)
        spawn_pos = (x, y)
        
        # Enemy 생성 시 필요한 sprite group 목록 전달
        sprite_groups = [self.all_sprites, self.enemy_group]
        
        # Enemy 인스턴스 생성
        Enemy(spawn_pos, enemy_type, self.game.asset_manager, self.player, sprite_groups)
        print(f"Spawning '{enemy_type}' at {spawn_pos} from network event.")
        
    def update(self, dt):
        """Update gameplay state"""
        # Don't update if game is won or player is dead
        if self.game_won or self.player.is_dead:
            return
            
        # Update all sprites
        self.all_sprites.update(dt)
        
        # Update wave manager (handles enemy spawning)
        self.wave_manager.update(dt)
        
        # Check for victory condition
        wave_info = self.wave_manager.get_wave_info()
        if wave_info['all_waves_complete']:
            self.game_won = True
            
        # Collision detection
        self.check_collisions()
        
    def check_collisions(self):
        """Handle all collision detection"""
        # Player bullets vs enemies
        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, False)
        for bullet, enemies in hits.items():
            for enemy in enemies:
                if enemy.take_damage():
                    self.score += enemy.get_score_value()
                    
        # Player vs enemies (contact damage)
        hits = pygame.sprite.spritecollide(self.player, self.enemy_group, False)
        if hits and not self.player.invulnerable:
            self.player.take_damage(30)  # Heavy damage from enemy contact
            # Remove one enemy on contact
            hits[0].kill()
            
        # Player vs enemy bullets
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullet_group, True)
        if hits and not self.player.invulnerable:
            for bullet in hits:
                self.player.take_damage(15)  # Moderate damage from bullets
            
    def draw(self, screen):
        """Draw gameplay state"""
        # Clear screen
        screen.fill(BLACK)
        
        # Draw all sprites except player
        for sprite in self.all_sprites:
            if sprite != self.player:
                screen.blit(sprite.image, sprite.rect)
        
        # Draw player with special handling for invulnerability
        self.player.draw(screen)
        
        # Draw UI
        self.draw_ui(screen)
        
        # Draw boss health bar if in boss battle
        wave_info = self.wave_manager.get_wave_info()
        if wave_info['is_boss_wave'] and wave_info['boss_enemy']:
            wave_info['boss_enemy'].draw_health_bar(screen)
        
    def draw_ui(self, screen):
        """Draw user interface"""
        font = self.game.asset_manager.get_font('score')
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw weapon level
        weapon_text = font.render(f"Weapon: {self.player.weapon_level}", True, WHITE)
        screen.blit(weapon_text, (10, 40))
        
        # Draw health bar
        health_bar_width = 200
        health_bar_height = 20
        health_x = 10
        health_y = 70
        
        # Background (red)
        health_bg_rect = pygame.Rect(health_x, health_y, health_bar_width, health_bar_height)
        pygame.draw.rect(screen, (100, 0, 0), health_bg_rect)
        
        # Health (green)
        health_percent = self.player.health / self.player.max_health
        health_width = int(health_bar_width * health_percent)
        if health_width > 0:
            health_rect = pygame.Rect(health_x, health_y, health_width, health_bar_height)
            pygame.draw.rect(screen, (0, 200, 0), health_rect)
        
        # Health bar border
        pygame.draw.rect(screen, WHITE, health_bg_rect, 2)
        
        # Health text
        health_text = font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (health_x + health_bar_width + 10, health_y))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 100))
        
        # Draw wave information
        wave_info = self.wave_manager.get_wave_info()
        wave_text = font.render(f"Wave {wave_info['wave_number']}/{wave_info['max_waves']}: {wave_info['wave_name']}", True, WHITE)
        screen.blit(wave_text, (10, 130))
        
        if wave_info['is_boss_wave']:
            # Boss battle specific info
            if wave_info['boss_enemy']:
                boss_status = "Boss Battle in Progress!"
                boss_status_color = (255, 255, 0)  # Yellow
            else:
                boss_status = "Boss Defeated!"
                boss_status_color = (0, 255, 0)  # Green
            boss_text = font.render(boss_status, True, boss_status_color)
            screen.blit(boss_text, (10, 160))
        else:
            # Regular wave info
            enemies_text = font.render(f"Enemies: {wave_info['enemies_alive']} active, {wave_info['enemies_remaining']} remaining", True, WHITE)
            screen.blit(enemies_text, (10, 160))
            
            # Wave progress bar (only for regular waves)
            if wave_info['wave_active']:
                progress_width = 200
                progress_height = 15
                progress_x = 10
                progress_y = 190
                
                # Background
                progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
                pygame.draw.rect(screen, (50, 50, 50), progress_bg)
                
                # Progress
                progress_percent = wave_info['progress'] / 100
                progress_fill_width = int(progress_width * progress_percent)
                if progress_fill_width > 0:
                    progress_rect = pygame.Rect(progress_x, progress_y, progress_fill_width, progress_height)
                    pygame.draw.rect(screen, (0, 150, 255), progress_rect)
                
                # Border
                pygame.draw.rect(screen, WHITE, progress_bg, 2)
                
                # Progress text
                progress_text = font.render(f"Wave Progress: {int(wave_info['progress'])}%", True, WHITE)
                screen.blit(progress_text, (progress_x + progress_width + 10, progress_y - 2))
        
        # Wave transition message
        if wave_info['in_transition']:
            if wave_info['wave_number'] % 5 == 0:
                # Boss defeated message
                transition_text = font.render(f"BOSS DEFEATED!", True, (255, 215, 0))  # Gold
                transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(transition_text, transition_rect)
                
                bonus_text = font.render(f"Wave {wave_info['wave_number']} Complete!", True, (0, 255, 0))
                bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
                screen.blit(bonus_text, bonus_rect)
            else:
                transition_text = font.render(f"WAVE {wave_info['wave_number']} COMPLETE!", True, (0, 255, 0))
                transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(transition_text, transition_rect)
            
            # Check if next wave is a boss wave
            next_wave = wave_info['wave_number'] + 1
            if next_wave % 5 == 0:
                next_wave_text = font.render(f"BOSS INCOMING...", True, (255, 0, 0))  # Red warning
            else:
                next_wave_text = font.render(f"Next Wave Starting...", True, WHITE)
            next_wave_rect = next_wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(next_wave_text, next_wave_rect)
        
        # Visual feedback for invulnerability
        if self.player.invulnerable:
            inv_text = font.render("INVULNERABLE", True, (255, 255, 0))
            screen.blit(inv_text, (10, 220))
            
        # Game over screen
        if self.player.is_dead:
            self.draw_game_over(screen)
        elif self.game_won:
            self.draw_game_success(screen)
            
    def draw_game_over(self, screen):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Game over text
        title_font = self.game.asset_manager.get_font('title')
        score_font = self.game.asset_manager.get_font('score')
        
        game_over_text = title_font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        
        final_score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(final_score_text, final_score_rect)
        
        restart_text = score_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)
    
    def draw_game_success(self, screen):
        """Draw victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Victory text
        title_font = self.game.asset_manager.get_font('title')
        score_font = self.game.asset_manager.get_font('score')
        
        victory_text = title_font.render("VICTORY!", True, (0, 255, 0))  # Green for success
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(victory_text, victory_rect)
        
        # Success message
        success_text = score_font.render("Congratulations! You saved the galaxy!", True, (255, 215, 0))  # Gold
        success_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(success_text, success_rect)
        
        # All waves completed
        waves_text = score_font.render("All 10 waves completed!", True, WHITE)
        waves_rect = waves_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(waves_text, waves_rect)
        
        # Final score
        final_score_text = score_font.render(f"Final Score: {self.score}", True, (255, 255, 0))  # Yellow
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(final_score_text, final_score_rect)
        
        # Restart instructions
        restart_text = score_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(restart_text, restart_rect)


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        
    def handle_events(self, events):
        """Handle menu events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.state_manager.change_state('gameplay')
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False
                    
    def update(self, dt):
        """Update menu state"""
        pass
        
    def draw(self, screen):
        """Draw menu state"""
        screen.fill(BLACK)
        
        font = self.game.asset_manager.get_font('title')
        title_text = font.render("STRIKER 1945", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title_text, title_rect)
        
        font = self.game.asset_manager.get_font('score')
        start_text = font.render("Press SPACE to start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(start_text, start_rect)
        
        quit_text = font.render("Press ESC to quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(quit_text, quit_rect)


class StateManager:
    def __init__(self, game):
        self.game = game
        self.states = {
            'menu': MenuState(game),
            'gameplay': GameplayState(game)
        }
        self.current_state = self.states['menu']
        
    def change_state(self, state_name):
        """Change to a different state"""
        if state_name in self.states:
            if state_name == 'gameplay':
                # Create a new gameplay state each time
                self.states['gameplay'] = GameplayState(self.game)
            self.current_state = self.states[state_name]