import pygame
import time
from settings import *

# --- Базовий клас Сутності ---
class Entity:
    # Ініціалізація сутності
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
    # Малювання сутності
    def draw(self, surface):
        surface.blit(self.image, (self.x * CELL_SIZE, self.y * CELL_SIZE))

# --- Клас Бомби ---
class Bomb(Entity):
    def __init__(self, x, y, image, wave_image, power):
        super().__init__(x, y, image)
        self.wave_image = wave_image
        self.power = power
        self.spawn_time = time.time()
        self.fuse_duration = 3.0
        self.explosion_duration = 0.5
        self.exploded = False
        self.finished = False
        self.explosion_tiles = []
        self.explosion_start_time = 0

    # Оновлення стану бомби
    def update(self, grid_map):
        current_time = time.time()

        # Час вибухати
        if not self.exploded and current_time - self.spawn_time >= self.fuse_duration:
            self.explode(grid_map)

        # Час зникати
        if self.exploded and current_time - self.explosion_start_time >= self.explosion_duration:
            self.finished = True

    # Логіка вибуху
    def explode(self, grid_map):
        self.exploded = True
        self.explosion_start_time = time.time()
        # Логіка розрахунку клітинок вибуху
        self.explosion_tiles = [(self.y, self.x)]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Розповсюдження вибуху в усі чотири сторони
        for dy, dx in directions:
            for step in range(1, self.power + 1):
                ny, nx = self.y + dy * step, self.x + dx * step
                # Перевірка меж карти
                if not (0 <= ny < len(grid_map) and 0 <= nx < len(grid_map[0])):
                    break
                tile = grid_map[ny][nx]
                # Блокування вибуху каменем
                if tile == "#": 
                    break
                # Блокування вибуху руйнівною стіною, але вона знищується
                self.explosion_tiles.append((ny, nx))  
                
    # Малювання бомби та вибуху
    def draw(self, surface):
        if not self.exploded:
            super().draw(surface)
        else:
            # Малюємо вибух
            for ey, ex in self.explosion_tiles:
                surface.blit(self.wave_image, (ex * CELL_SIZE, ey * CELL_SIZE))
            if self.finished:
                self.explosion_tiles = []

# --- Клас Гравця ---
class Player(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.max_bombs = 1
        self.bomb_power = 1
        self.active_bombs = []
        self.is_dead = False
        self.has_won = False

    # Обробка вводу гравця
    def handle_input(self, event, grid_map, bomb_images):
        if self.is_dead or self.has_won: return

        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            elif event.key == pygame.K_DOWN: dy = 1
            elif event.key == pygame.K_LEFT: dx = -1
            elif event.key == pygame.K_RIGHT: dx = 1
            elif event.key == pygame.K_SPACE:
                self.place_bomb(bomb_images)

            if dx != 0 or dy != 0:
                self.move(dx, dy, grid_map)

    # Рух гравця
    def move(self, dx, dy, grid_map):
        nx, ny = self.x + dx, self.y + dy
        # Перевірка меж карти та колізій
        if 0 <= ny < len(grid_map) and 0 <= nx < len(grid_map[0]):
            tile = grid_map[ny][nx]
            # Блокування руху каменем, руйнівною стіною або бонусом
            if tile in ["#", "X", "b", "w", "d"]:
                return 
            self.x, self.y = nx, ny
            # Обробка бонусів та виходу
            self.check_tile_interaction(grid_map, ny, nx)
  
    # Перевірка взаємодії з клітинкою
    def check_tile_interaction(self, grid_map, r, c):
        tile = grid_map[r][c]
        if tile == "D": 
            self.has_won = True # Вихід
        elif tile == "B": 
            self.max_bombs += 1 # Bomb Bonus
            grid_map[r][c] = " "
        elif tile == "W": 
            self.bomb_power += 1 # Wave Bonus
            grid_map[r][c] = " "

    # Розміщення бомби гравцем
    def place_bomb(self, images):
        # Перевірка на максимальну кількість бомб
        if len(self.active_bombs) < self.max_bombs:
            new_bomb = Bomb(self.x, self.y, images['bomb'], images['wave'], self.bomb_power)
            self.active_bombs.append(new_bomb)