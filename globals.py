import pygame as pg
from pygame.locals import *
from classes_package import *

dt = 0

player = pg.sprite.GroupSingle()
player.add(Player())

map = Map()