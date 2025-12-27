import random
from settings import *

class Level:
    def __init__(self, width, height, level_file=None):
        self.width = width
        self.height = height
        self.grid = []
        if level_file:
            self.load_from_file(level_file)
        else:
            self.generate()

    def generate(self):
        self.grid = [["#" for _ in range(self.width)] for _ in range(self.height)]
        
        # Створення сітки
        for i in range(self.height):
            for j in range(self.width):
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    self.grid[i][j] = "#"
                elif i % 2 == 1 or j % 2 == 1:
                    self.grid[i][j] = " "
                else:
                    self.grid[i][j] = "#"
        # Стіни X
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == " " and random.random() < 0.4:
                    self.grid[i][j] = "X"
        
        # Вихід та бонуси 
        self.place_object("d", 1) # Door 
        self.place_object("b", 3) # Bomb bonus
        self.place_object("w", 3) # Wave bonus
        
        # Стартова зона
        self.grid[1][1] = " "
        self.grid[2][1] = " "
        self.grid[1][2] = " "

    def place_object(self, char, count):
        placed = 0
        while placed < count:
            r = random.randint(1, self.height-2)
            c = random.randint(1, self.width-2)
            if self.grid[r][c] == "X":
                if char == "d": self.grid[r][c] = "d" 
                elif char == "b": self.grid[r][c] = "b" 
                elif char == "w": self.grid[r][c] = "w" 
                placed += 1

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.grid = [list(line.strip()) for line in f]
            self.height = len(self.grid)
            self.width = len(self.grid[0])
        except FileNotFoundError: 
            self.generate()

    def update_grid_after_explosion(self, tiles):
        for r, c in tiles:
            if self.grid[r][c] == "X": self.grid[r][c] = " "
            elif self.grid[r][c] == "d": self.grid[r][c] = "D" 
            elif self.grid[r][c] == "b": self.grid[r][c] = "B" 
            elif self.grid[r][c] == "w": self.grid[r][c] = "W"

    def draw(self, surface, images):
        for i in range(self.height):
            for j in range(self.width):
                x, y = j * CELL_SIZE, i * CELL_SIZE
                tile = self.grid[i][j]
                
                # Малюємо фон (трава/порожньо)
                surface.blit(images["empty"], (x, y))
                
                if tile == "#": surface.blit(images["stone"], (x, y))
                elif tile == "X": surface.blit(images["wall"], (x, y))
                elif tile in ["d", "b", "w"]: surface.blit(images["wall"], (x, y)) # Приховані
                elif tile == "D": surface.blit(images["door"], (x, y))
                elif tile == "B": surface.blit(images["bomb_bonus"], (x, y))
                elif tile == "W": surface.blit(images["wave_bonus"], (x, y))