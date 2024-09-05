import pygame as pg
from pygame.locals import *
from classes_package import *

dt = 0

player = pg.sprite.GroupSingle()
player.add(Player())

map = Map()


# Every singleton should have a lifecycle hook called on_globals_loaded which fires once every singleton has been initialized
player.sprite.on_globals_loaded()
map.on_globals_loaded()