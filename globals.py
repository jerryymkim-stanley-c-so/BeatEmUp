import pygame as pg
from pygame.locals import *

from global_constants import *
from classes_package import *

dt = 0

player = pg.sprite.GroupSingle()
player.add(Player())

map = Map()

def master_draw():
    screen.fill("black")
    map.blit_map()
    # map.blit_player_shadow()
    map.draw_birds_eye_view()

    # player.draw(screen)
    player.update()
    map.blit_fps()
    map.blit_debug()
