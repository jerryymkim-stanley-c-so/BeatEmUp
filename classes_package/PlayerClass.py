import pygame as pg
from pygame.locals import *

from global_constants import *
from .UsefulFunctions import *
# from .MapClass import Map
import globals

PLAYER_WIDTH = 50
PLAYER_HEIGTH = 100
PLAYER_SIZE = (PLAYER_WIDTH, PLAYER_HEIGTH)
PLAYER_MVMT_SPD = 150
PLAYER_JUMP_SPD = -15
PLAYER_GRAVITY_SPD = 1

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.dt = None

        self.image = pg.Surface(PLAYER_SIZE)
        self.image.fill(color=(255,0,0))
        pg.draw.rect(self.image, (255,255,255), self.image.get_frect(topleft=(0,0)), 1)
        self.rect = self.image.get_frect(center=SCREEN_CENTER)

        self.isJumping = False
        self.gravity = 0
        self.shadow_y = self.rect.bottom
        self.shadow_dot = (self.rect.centerx, self.shadow_y)

    def movement(self):
        keys = pg.key.get_pressed()

        # Movement
        if keys[K_a]:
            self.rect.x -= PLAYER_MVMT_SPD * self.dt
            
        if keys[K_d]:
            self.rect.x += PLAYER_MVMT_SPD * self.dt
        if not self.isJumping and keys[K_w]:
            self.rect.y -= PLAYER_MVMT_SPD * self.dt
        if not self.isJumping and keys[K_s]:
            self.rect.y += PLAYER_MVMT_SPD * self.dt

        # Border Collision
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        # if self.rect.bottom >= map.get_map_bottom():
        #     self.rect.bottom = map.get_map_bottom()
        # if not self.isJumping and self.rect.bottom <= map.get_map_top():
        #     self.rect.bottom = map.get_map_top()

    def jumping(self):
        keys = pg.key.get_pressed()

        pg.draw.circle(screen, 'yellow', self.shadow_dot, 3)

        if not self.isJumping and keys[K_SPACE]:
            self.isJumping = True
            self.gravity = PLAYER_JUMP_SPD

        if self.isJumping:
            self.rect.y += self.gravity
            self.gravity += PLAYER_GRAVITY_SPD

            if self.rect.bottom > self.shadow_y:
                self.rect.bottom = self.shadow_y
                self.isJumping = False
                self.gravity = 0

    def update_shadow(self):
        # This needs to change when I implement elevations
        if not self.isJumping:
            self.shadow_y = self.rect.bottom
        self.shadow_dot = (self.rect.centerx, self.shadow_y)

    def update_dt(self):
        self.dt = globals.dt

    def update(self):
        self.update_dt()
        self.update_shadow()

        self.movement()
        self.jumping()
