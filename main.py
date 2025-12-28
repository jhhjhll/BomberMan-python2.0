import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
import pygame
import sys
from settings import *
from game_states import MenuState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_assets()
        self.state = MenuState(self) # Початковий стан

    # Завантаження активів
    def load_assets(self):
        def load_img(path, color):
            try:
                img = pygame.image.load(path)
            except:
                img = pygame.Surface((CELL_SIZE, CELL_SIZE))
                img.fill(color)
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        # Завантаження зображень
        self.images = {
            "stone": load_img("Image/Stone.jpg", (50, 50, 50)),
            "empty": load_img("Image/Empty.jpg", (34, 139, 34)),
            "wall": load_img("Image/Wall.jpg", (139, 69, 19)),
            "pers": load_img("Image/Pers.jpg", (255, 255, 255)),
            "door": load_img("Image/Door.jpg", (0, 0, 0)),
            "bomb": load_img("Image/BOMB.jpg", (0, 0, 0)),
            "wave": load_img("Image/Wave.jpg", (255, 165, 0)),
            "bomb_bonus": load_img("Image/BombBonus.jpg", (255, 0, 0)),
            "wave_bonus": load_img("Image/WaveBonus.jpg", (0, 0, 255))
        }
    # Зміна стану гри
    def change_state(self, new_state):
        self.state = new_state

    # Основний цикл гри
    def run(self):
        while self.running:
            # 1. Події
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.state.handle_events(event)
            
            # 2. Логіка
            self.state.update()
            # 3. Малювання
            self.state.draw()
            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()