import pygame as pg
from pygame.locals import *

import globals
from global_constants import *
from .UsefulFunctions import *

class AllSprites(pg.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pg.Vector2()

    def on_globals_loaded(self):
        pass

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - SCREEN_WIDTH / 2)
        self.offset.y = -(target_pos[1] - SCREEN_HEIGHT / 2)

        for sprite in self:
            screen.blit(sprite.image, sprite.rect.topleft + self.offset)