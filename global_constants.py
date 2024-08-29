import pygame as pg
from pygame.locals import *

# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_CENTER = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
FPS = 60

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


