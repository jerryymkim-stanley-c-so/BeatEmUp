import pygame as pg
from pygame.locals import *
from classes_package import *

dt = 0

map = Map()

all_sprites = AllSprites()

player = Player((all_sprites))

# TODO: REMOVE THIS
# all_entities = [ player ]
for enemy_data in map.enemy_locations:
  enemy = Enemy((all_sprites), enemy_data)
  # all_entities.append(enemy)

camera = Camera()

# Every singleton should have a lifecycle hook called on_globals_loaded which fires once every singleton has been initialized
map.on_globals_loaded()
all_sprites.on_globals_loaded()
player.on_globals_loaded()
camera.on_globals_loaded()