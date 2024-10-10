import pygame as pg
from pygame.locals import *
from classes_package import *

dt = 0

map = Map()

player = pg.sprite.GroupSingle()
player.add(Player())


# Every singleton should have a lifecycle hook called on_globals_loaded which fires once every singleton has been initialized
map.on_globals_loaded()
player.sprite.on_globals_loaded()