import pygame as pg
from pygame.locals import *

import globals
from global_constants import *
from .UsefulFunctions import *
# from .MapClass import Map

# PLAYER_WIDTH = 50
# PLAYER_HEIGHT = 100
PLAYER_SIZE = (PLAYER_WIDTH, PLAYER_HEIGHT)
# PLAYER_MVMT_SPD = 150
PLAYER_MVMT_X_SPD = 5
PLAYER_MVMT_Y_SPD = 3
PLAYER_JUMP_SPD = 15
# PLAYER_GRAVITY_RATE = 1
PLAYER_GRAVITY_RATE = -1

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.dt = None

        self.abstraction_x = 0
        self.abstraction_y = 0
        self.abstraction_h = 0

        self.image = pg.Surface(PLAYER_SIZE)
        self.image.fill(color=(255,0,0))
        pg.draw.rect(self.image, (255,255,255), self.image.get_frect(topleft=(0,0)), 1)
        # self.rect = self.image.get_frect(center=SCREEN_CENTER)
        self.rect = self.image.get_frect(center=(0,0))

        self.is_jumping = False
        self.vertical_speed = 0
        self.horizontal_speed = 0
        self.depth_speed = 0
        # self.shadow_y = self.rect.bottom
        # self.shadow_dot = (self.rect.centerx, self.shadow_y)
        self.shadow_h = 0
        self.shadow_projection = (0, 0)

    def on_globals_loaded(self):
        
        # Reposition the player at the start location
        self.abstraction_x = globals.map.player_start_x
        self.abstraction_y = globals.map.player_start_y
        self.abstraction_h = globals.map.player_start_h

    def apply_movement(self):
        self.abstraction_x += self.horizontal_speed * self.dt
        self.abstraction_y += self.depth_speed * self.dt

        self.horizontal_speed = 0
        self.depth_speed = 0

    def apply_gravity(self):
        # self.abstraction_h += self.vertical_speed
        self.abstraction_h += self.vertical_speed * self.dt

        # if self.is_jumping:
        if self.abstraction_h > self.shadow_h:
            # self.rect.y += self.vertical_speed
            self.vertical_speed += PLAYER_GRAVITY_RATE

        # Check for landing
        # if self.rect.bottom > self.shadow_y:
        if self.abstraction_h < self.shadow_h:
            self.abstraction_h = self.shadow_h
            self.is_jumping = False
            self.vertical_speed = 0

    def resolve_movement(self):
        keys = pg.key.get_pressed()

        # Movement
        if keys[K_a]:
            # self.rect.x -= PLAYER_MVMT_SPD * self.dt
            self.horizontal_speed = -PLAYER_MVMT_X_SPD
            
        if keys[K_d]:
            # self.rect.x += PLAYER_MVMT_SPD * self.dt
            self.horizontal_speed = PLAYER_MVMT_X_SPD
        # if not self.is_jumping and keys[K_w]:
        if keys[K_w]:
            # self.rect.y -= PLAYER_MVMT_SPD * self.dt
            self.depth_speed = -PLAYER_MVMT_Y_SPD
        # if not self.is_jumping and keys[K_s]:
        if keys[K_s]:
            # self.rect.y += PLAYER_MVMT_SPD * self.dt
            self.depth_speed = PLAYER_MVMT_Y_SPD

        # # Border Collision
        # if self.rect.right >= SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        # if self.rect.left <= 0:
        #     self.rect.left = 0
        # if self.rect.bottom >= map.get_map_bottom():
        #     self.rect.bottom = map.get_map_bottom()
        # if not self.is_jumping and self.rect.bottom <= map.get_map_top():
        #     self.rect.bottom = map.get_map_top()

    def resolve_jumping(self):
        keys = pg.key.get_pressed()

        if not self.is_jumping and keys[K_SPACE]:
            self.is_jumping = True
            self.vertical_speed = PLAYER_JUMP_SPD


    def update_sprite_position(self):
        self.rect.center = projection_coords_by_abstraction_coords(self.abstraction_x, self.abstraction_y, self.abstraction_h)
        self.rect.y -= PLAYER_HEIGHT // 2
        # print(f"x: {self.rect.x} | y: {self.rect.y}")
        # self.shadow_y = self.rect.bottom
        # self.shadow_dot = (self.rect.centerx, self.shadow_y)

    def update_shadow(self):
        # if not self.is_jumping:
        #     # self.shadow_y = self.rect.bottom
        # self.shadow_dot = (globals.player.sprite.rect.centerx, self.shadow_y)

        # Scan down from current position to update shadow dot elevation
        self.shadow_h = min(int(self.abstraction_h), globals.map.map_dimensions_height - 1)  # shadow cannot exceed highest map layer
        x, y = self.abstraction_x, self.abstraction_y
        x_frac, y_frac = x - int(x), y - int(y)
        # TODO: what about half-tiles? need a function to determine if your current float pos falls through or not
        while (self.shadow_h - 1) in globals.map.map_data \
            and (globals.map.map_data[self.shadow_h][int(y)][int(x)] == MAP_EMPTY \
                 or (globals.map.map_data[self.shadow_h][int(y)][int(x)] == MAP_7 and x_frac > 1-y_frac) \
                 or (globals.map.map_data[self.shadow_h][int(y)][int(x)] == MAP_F and y_frac > x_frac) \
                 or (globals.map.map_data[self.shadow_h][int(y)][int(x)] == MAP_J and y_frac < x_frac) \
                 or (globals.map.map_data[self.shadow_h][int(y)][int(x)] == MAP_L and x_frac < 1-y_frac)):
            self.shadow_h -= 1
        
        # draw green dot at shadow
        self.shadow_projection = projection_coords_by_abstraction_coords(self.abstraction_x, self.abstraction_y, self.shadow_h)
        pg.draw.circle(screen, 'green', self.shadow_projection, 3)

    def update_dt(self):
        self.dt = globals.dt

    def update(self):
        self.update_dt()
        self.update_shadow()
        self.apply_movement()
        self.apply_gravity()
        self.update_sprite_position()

        # Resolve inputs
        self.resolve_movement()
        self.resolve_jumping()
