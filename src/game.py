import pygame
import sys
from src.settings import *
from src.asset_manager import AssetManager
from src.states import StateManager
from src.network_monitor import NetworkMonitor  # NetworkMonitor 임포트

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Initialize audio (optional - skip if no audio device available)
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Warning: No audio device available, running without sound")
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Striker 1945")
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Asset manager
        self.asset_manager = AssetManager()
        self.asset_manager.load_all()
        
        # State manager
        self.state_manager = StateManager(self)
        
        # --- 네트워크 모니터 시작 ---
        self.network_monitor = NetworkMonitor()
        self.network_monitor.start()
        
    def run(self):
        """Main game loop"""
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Update current state
            self.state_manager.current_state.handle_events(events)
            self.state_manager.current_state.update(dt)
            
            # Draw current state
            self.state_manager.current_state.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
        # --- 네트워크 모니터 종료 ---
        self.network_monitor.stop()
        
        # Quit
        pygame.quit()
        sys.exit()