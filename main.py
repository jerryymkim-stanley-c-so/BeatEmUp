import math
import pygame as pg
from pygame.locals import *
from sys import exit

pg.init()

import globals
from global_constants import *

while True:
    for event in pg.event.get():
        # Quit
        if event.type == QUIT:
            pg.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit()
                exit()

            # Debug Keys
            elif event.key == K_UP: globals.map.curr_layer += 1
            elif event.key == K_DOWN and globals.map.curr_layer > 0: globals.map.curr_layer -= 1
            elif event.key == K_p: globals.map.wait_on = not globals.map.wait_on


    # screen.fill("black")
    # globals.map.blit_map()
    # # globals.map.blit_player_shadow()
    # globals.map.draw_birds_eye_view()

    # # globals.player.draw(screen)
    # globals.player.update()
    # globals.map.blit_fps()
    # globals.map.blit_debug()
    globals.master_draw()

    pg.display.update()
    globals.dt = clock.tick(FPS) / 1000