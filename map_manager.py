import random
from settings import *

class Level:
    def __init__(self, width, height, level_file=None):
        # Випадкові розміри, якщо обрано випадкову генерацію
        if width is None:
            self.width = random.randrange(9, 32, 2) 
        else:
            self.width = width
        if height is None:
            self.height = random.randrange(9, 18, 2) 
        else:
            self.height = height
        self.grid = []
        # Завантаження рівня з файлу або випадкова генерація
        if level_file:
            self.load_from_file(level_file)
        else:
            self.generate()

    # Випадкова генерація рівня
    def generate(self):
        # Ініціалізація порожньої сітки
        self.grid = [["#" for _ in range(self.width)] for _ in range(self.height)]
        # 1. Створення сітки статичних каменів і порожніх клітинок
        for i in range(self.height):
            for j in range(self.width):
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    self.grid[i][j] = "#"
                elif i % 2 == 1 or j % 2 == 1:
                    self.grid[i][j] = " "
                else:
                    self.grid[i][j] = "#"
        # 2. Створення руйнівних стін з імовірністю 40%
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == " " and random.random() < 0.4:
                    self.grid[i][j] = "X"
        
        # 3. ЛОГІКА БОНУСІВ
        # кількість скільки що руйнуються
        destructible_walls = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == "X":
                    destructible_walls.append((y, x))
        if not destructible_walls: return
        # кількість бонусів (10% від руйнівних стін)
        num_bonuses = max(1, int(len(destructible_walls) * 0.10))
        # Перемішуємо список стін для випадкового вибору
        random.shuffle(destructible_walls)
        # Ставимо двері (перша руйнівна стіна зі списку)
        dy, dx = destructible_walls.pop()
        self.grid[dy][dx] = "d" 
        # Розставляємо бонуси
        for i in range(num_bonuses):
            if not destructible_walls: break
            by, bx = destructible_walls.pop()
            bonus_type = "b" if random.random() < 0.5 else "w"
            self.grid[by][bx] = bonus_type
        # Стартова зона гравця
        self.grid[1][1] = " "
        self.grid[2][1] = " "
        self.grid[1][2] = " "

    # Завантаження рівня з файлу
    def load_from_file(self, filename): 
        try:
            with open(filename, 'r') as f:
                self.grid = [list(line.strip()) for line in f]
            self.height = len(self.grid)
            self.width = len(self.grid[0])
        except FileNotFoundError: 
            self.generate()

    # Оновлення сітки після вибуху бомби
    def update_grid_after_explosion(self, tiles):
        for r, c in tiles:
            if self.grid[r][c] == "X": self.grid[r][c] = " "
            elif self.grid[r][c] == "d": self.grid[r][c] = "D" 
            elif self.grid[r][c] == "b": self.grid[r][c] = "B" 
            elif self.grid[r][c] == "w": self.grid[r][c] = "W"

    # Малювання рівня
    def draw(self, surface, images):
        for i in range(self.height):
            for j in range(self.width):
                x, y = j * CELL_SIZE, i * CELL_SIZE
                tile = self.grid[i][j]
                # Малюємо фон 
                surface.blit(images["empty"], (x, y))
                # Малюємо відповідний елемент на сітці
                if tile == "#": surface.blit(images["stone"], (x, y))
                elif tile == "X": surface.blit(images["wall"], (x, y))
                elif tile in ["d", "b", "w"]: surface.blit(images["wall"], (x, y))
                elif tile == "D": surface.blit(images["door"], (x, y))
                elif tile == "B": surface.blit(images["bomb_bonus"], (x, y))
                elif tile == "W": surface.blit(images["#wave_bonus"], (x, y))