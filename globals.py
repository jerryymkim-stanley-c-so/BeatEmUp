import pygame as pg
from pygame.locals import *
from classes_package import *

dt = 0

map = Map()

player = pg.sprite.GroupSingle()
player.add(Player())

# TODO: REMOVE THIS
all_entities = [ player ]
for enemy_data in map.enemy_locations:
  enemy = pg.sprite.GroupSingle()
  enemy.add(Enemy(enemy_data))
  all_entities.append(enemy)

camera = Camera()

# Every singleton should have a lifecycle hook called on_globals_loaded which fires once every singleton has been initialized
map.on_globals_loaded()
player.sprite.on_globals_loaded()
camera.on_globals_loaded()