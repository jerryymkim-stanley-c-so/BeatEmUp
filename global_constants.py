import pygame as pg
from pygame.locals import *
from sys import intern

# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
FPS = 60

MAP_EMPTY = '.'
MAP_7 = '7'
MAP_F = 'F'
MAP_J = 'J'
MAP_L = 'L'

PROJECTION_TILE_X_OFFSET = 50  # tile size in px, basically
PROJECTION_TILE_Y_OFFSET = 50  # tile size in px (actual floor portion only), basically
PROJECTION_GROUND_LEVEL_ORIGIN = 0, SCREEN_HEIGHT//2  # the place on the screen where the top left ground level should be. revisit this later

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


cube = intern("cube")
half_7 = intern("half_7")
half_F = intern("half_F")
half_J = intern("half_J")
half_L = intern("half_L")