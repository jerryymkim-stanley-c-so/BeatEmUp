import pygame as pg
from pygame.locals import *
from sys import intern

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
FPS = 60

MAP_EMPTY = '.'
MAP_FLOOR = '1'
MAP_7 = '7'
MAP_F = 'F'
MAP_J = 'J'
MAP_L = 'L'

PROJECTION_TILE_X_OFFSET = 50  # tile size in px, basically
PROJECTION_TILE_Y_OFFSET = 50  # tile size in px (actual floor portion only), basically
PROJECTION_GROUND_LEVEL_ORIGIN = 0, SCREEN_HEIGHT//2  # the place on the screen where the top left ground level should be. revisit this later. possibly name this something like 'HORIZON_TOP_LEFT'

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


# sys.intern makes a string more performant.
# "Interning strings is useful to gain a little performance on dictionary lookup – if the
# keys in a dictionary are interned, and the lookup key is interned, the key comparisons
# (after hashing) can be done by a pointer compare instead of a string compare."

cube = intern("cube")
half_7 = intern("half_7")
half_F = intern("half_F")
half_J = intern("half_J")
half_L = intern("half_L")