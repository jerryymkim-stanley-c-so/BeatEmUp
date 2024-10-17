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
            elif event.key == K_p: globals.map.wait_on = not globals.map.wait_on

    screen.fill("black")

    for sprite in globals.all_sprites:
        sprite.update()

    globals.camera.draw()
    pg.display.update()

    globals.dt = clock.tick(FPS) / 1000