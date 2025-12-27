# game_states.py
import pygame
import sys
import time
from settings import *
from entities import Player
from map_manager import Level

# --- Базовий клас Стану ---
class State:
    def __init__(self, game):
        self.game = game # Посилання на головний об'єкт гри
    
    def handle_events(self, event):
        pass
    
    def update(self):
        pass
    
    def draw(self):
        pass

# --- Стан: Головне меню ---
class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.game.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.font = pygame.font.Font(None, 50)
        # Проста структура кнопок
        self.options = [
            ("Кампанія", self.start_campaign),
            ("Випадковий рівень", self.start_random),
            ("Вихід", self.exit_game)
        ]
        self.selected_index = 0

    def start_campaign(self):
        # Перемикаємо на екран вибору рівня
        self.game.change_state(LevelSelectState(self.game))

    def start_random(self):
        # Одразу запускаємо гру
        self.game.change_state(GameplayState(self.game, random_gen=True))

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Проста логіка кліків (можна покращити клас Button)
            for i, (text, action) in enumerate(self.options):
                rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200 + i*70, 200, 50)
                if rect.collidepoint((mx, my)):
                    action()

    def draw(self):
        self.game.screen.fill(BLACK)
        title = self.font.render("BomberMan", True, YELLOW)
        self.game.screen.blit(title, (SCREEN_WIDTH//2 - 100, 100))

        mx, my = pygame.mouse.get_pos()
        for i, (text, _) in enumerate(self.options):
            rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 200 + i*70, 300, 50)
            color = LIGHT_BLUE if rect.collidepoint((mx, my)) else BLUE
            pygame.draw.rect(self.game.screen, color, rect, border_radius=10)
            
            label = pygame.font.Font(None, 36).render(text, True, WHITE)
            self.game.screen.blit(label, (rect.centerx - label.get_width()//2, rect.centery - label.get_height()//2))

# --- Стан: Вибір рівня ---
class LevelSelectState(State):
    def __init__(self, game):
        super().__init__(game)
        self.levels = [1, 2, 3, 4, 5]

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state(MenuState(self.game))
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, lvl in enumerate(self.levels):
                rect = pygame.Rect(60 + i*100, 150, 80, 80)
                if rect.collidepoint((mx, my)):
                    filename = f"level_{lvl}.txt"
                    self.game.change_state(GameplayState(self.game, level_file=filename))

    def draw(self):
        self.game.screen.fill(BLACK)
        draw_text = pygame.font.Font(None, 50).render("Select Level", True, YELLOW)
        self.game.screen.blit(draw_text, (SCREEN_WIDTH//2 - 100, 50))
        
        mx, my = pygame.mouse.get_pos()
        for i, lvl in enumerate(self.levels):
            rect = pygame.Rect(60 + i*100, 150, 80, 80)
            color = LIGHT_BLUE if rect.collidepoint((mx, my)) else BLUE
            pygame.draw.rect(self.game.screen, color, rect, border_radius=10)
            text = pygame.font.Font(None, 40).render(str(lvl), True, WHITE)
            self.game.screen.blit(text, (rect.centerx-10, rect.centery-10))

# --- Стан: Власне гра ---
class GameplayState(State):
    def __init__(self, game, level_file=None, random_gen=False):
        super().__init__(game)
        if random_gen:
            self.level = Level(15, 13)
        else:
            self.level = Level(15, 13, level_file)

        level_width_px = self.level.width * CELL_SIZE
        level_height_px = self.level.height * CELL_SIZE
        self.game.screen = pygame.display.set_mode((level_width_px, level_height_px))
            
        self.player = Player(1, 1, self.game.images['pers'])
        self.start_time = time.time()
        self.game_over = False
        self.end_game_time = 0

    def handle_events(self, event):
        self.player.handle_input(event, self.level.grid, self.game.images)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
             self.game.change_state(MenuState(self.game))

    def update(self):
        # 1. Логіка завершення гри
        if self.game_over:
            current_time = time.time()
            if current_time - self.end_game_time > 1: # Чекаємо 1 секунди
                self.game.change_state(MenuState(self.game)) 
            return

        # Оновлення бомб
        for bomb in self.player.active_bombs:
            bomb.update(self.level.grid)
            # Якщо бомба вибухнула і ще активна
            if bomb.exploded and not bomb.finished:
                self.level.update_grid_after_explosion(bomb.explosion_tiles)
                # Перевірка смерті гравця
                if (self.player.y, self.player.x) in bomb.explosion_tiles:
                    print("Game Over!")
                    self.game_over = True
                    self.end_game_time = time.time() # Засікаємо час смерті
        # Видаляємо старі бомби 
        self.player.active_bombs = [b for b in self.player.active_bombs if not b.finished]

        # Перевірка виграшу
        if self.player.has_won:
            print("You Win!")
            self.game_over = True
            self.end_game_time = time.time() # Засікаємо час перемоги

    def draw(self):
        self.game.screen.fill(BLACK)
        # 1. Малюємо карту
        self.level.draw(self.game.screen, self.game.images)
        # 2. Малюємо бомби
        for bomb in self.player.active_bombs:
            bomb.draw(self.game.screen)
        # 3. Малюємо гравця
        if not self.game_over or (int(time.time()*5) % 2 == 0): # Миготіння при смерті
             self.player.draw(self.game.screen)
        # 4. UI (Час)
        elapsed = int(time.time() - self.start_time)
        txt = pygame.font.Font(None, 36).render(f"Time: {elapsed}", True, BLACK)
        self.game.screen.blit(txt, (10, 10))