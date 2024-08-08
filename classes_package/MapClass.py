import pygame as pg
from pygame.locals import *

from global_constants import *
from .UsefulFunctions import *
import globals

from random import randint

MAP_HEIGHT = 400
PLAYER_SHADOW_WIDTH = 75
PLAYER_SHADOW_HEIGHT = 30
PLAYER_SHADOW_ALPHA = 100

MAP_STARTING_POS = (600, 340)
TILE_X_OFFSET = 76
TILE_Y_OFFSET = 30
TILE_ELEVATION_Y_OFFSET = 76
BIRDS_EYE_SCALE_DOWN_MULT = 5


class Map():
    def __init__(self):
        self.player = globals.player

        self.cube = pg.image.load('graphics/cube_testblock.png').convert_alpha()
        self.highlight_cube = pg.image.load('graphics/cube_highlighted_testblock.png').convert_alpha()
        self.cube.set_colorkey((255,255,255))
        self.highlight_cube.set_colorkey((255,255,255))
        self.tile_width = self.cube.get_width()
        self.tile_height = self.cube.get_height()

        self.font = pg.font.Font(None, 25)

        self.map_data = {}
        def create_map_data():
            map_data = {}

            f = open('map.txt')

            curr_layer = None
            for row in f.read().split('\n'):
                if 'Layer' in row:
                    curr_layer = row
                    map_data[curr_layer] = []
                elif row:
                    map_data[curr_layer].append([int(c) for c in row])

            # Alternate method of reading, By Stan
            # for layer_str in f.read().split('\n\n'):
            #     layer = layer_str.split('\n')
            #     curr_layer = layer[0]
            #     map_data[curr_layer] = []
            #     for i in range(1, len(layer)):
            #         row = layer[i]
            #         map_data[curr_layer].append([int(c) for c in row])
            f.close()
            return map_data
        self.map_data = create_map_data()

        # Print map_data
        # for key in self.map_data.keys():
        #     for row in self.map_data[key]:
        #         print(f'{key}: {row}')

        # Debug Variables
        self.curr_layer = 0
        self.curr_row = 0
        self.curr_col = 0
        self.wait_on = False

    def blit_debug(self):
        keys = pg.key.get_pressed()

        # Show Current Row
        curr_row_surf = self.font.render(f'Current Row: {int(self.curr_row)}', None, (255,255,255))
        curr_row_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT))
        screen.blit(curr_row_surf, curr_row_rect)
        # Height of Text
        text_height = curr_row_surf.get_height()

        # Show Current Col
        curr_col_surf = self.font.render(f'Current Col: {int(self.curr_col)}', None, (255,255,255))
        curr_col_rect = curr_col_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*1))
        screen.blit(curr_col_surf, curr_col_rect)

        # Show Current Layer
        curr_layer_surf = self.font.render(f'Current Layer: {int(self.curr_layer)}', None, (255,255,255))
        curr_layer_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*2))
        screen.blit(curr_layer_surf, curr_layer_rect)

    def blit_fps(self):
        fps_surf = self.font.render(f'FPS: {round(clock.get_fps())}', None, (255,255,255))
        screen.blit(fps_surf,(0,0))

    def blit_map(self):
        # Draw Tiles
        midbottom = self.player.sprite.shadow_dot
        bottom = self.player.sprite.shadow_y

        for layer, key in enumerate(self.map_data.keys()):
            for y, row in enumerate(self.map_data[key]):
                for x, tile in enumerate(row):
                    if tile:
                        rect = self.cube.get_frect(topleft=(MAP_STARTING_POS[0] + x*TILE_X_OFFSET - TILE_Y_OFFSET*y, MAP_STARTING_POS[1] + y*TILE_Y_OFFSET - layer*TILE_X_OFFSET))

                        # Highlight the tile the player is on
                        if rect.collidepoint(midbottom) and rect.top <= bottom <= rect.top + 32: screen.blit(self.highlight_cube, rect)
                        else: screen.blit(self.cube, rect)

                        if self.wait_on:
                            pg.time.wait(200)
                            pg.display.update()

                        # Draw Player at the correct time
                        if self.curr_row == y and self.curr_col == x:
                            globals.map.blit_player_shadow()
                            globals.player.draw(screen)



    def draw_birds_eye_view(self):
        # Offset is subtracted by TILE_Y_OFFSET because of the shift in the topleft corner of rhombus
        # Since it's 45 degrees, TILE_Y_OFFSET would be the same as making an 'X' offset by just that triangle's amount
        # Everything is divided by TILE_X_OFFSET to enumerate which tile the player is on
        # For example, if the player is on the 0th tile in the x-direction, the x_offset should be somewhere between 0.00 -- 1.00
        # The same logic applies for the y_offset, however the 'self.curr_layer*TILE_X_OFFSET' accounts for how high the player is in elevation
        x_offset_center = (self.player.sprite.rect.centerx - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        x_offset_left = (self.player.sprite.rect.left - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        x_offset_right = (self.player.sprite.rect.right - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        y_offset = (self.player.sprite.shadow_y - MAP_STARTING_POS[1] + self.curr_layer*TILE_X_OFFSET)/TILE_Y_OFFSET

        # These variables are to scale down the tiles to a smaller size
        width = self.tile_width/BIRDS_EYE_SCALE_DOWN_MULT
        height = self.tile_height/BIRDS_EYE_SCALE_DOWN_MULT

        for layer, key in enumerate(self.map_data.keys()):
            for y, row in enumerate(self.map_data[key]):
                for x, tile in enumerate(row):
                    if tile:
                        pg.draw.rect(screen, 'white', (20 + x*width, 20 + y*height, width, height), 1)

                        # Topographical heat map; the location of the surf is offsetted just a bit so that it doesn't cover the white outlines
                        if layer > 0:
                            surf = pg.Surface((width - 2, height - 2))
                            surf.fill('red')
                            surf.set_alpha(50)
                            screen.blit(surf, (22 + x*width, 21 + y*height))

        # Draw the Player's width in the orthogonal view
        left_point = (x_offset_left*width + 20 + width*y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET), y_offset*height + 20)
        right_point = (x_offset_right*width + 20 + width*y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET), y_offset*height + 20)
        pg.draw.line(screen, 'red', left_point, right_point, 3)

        # Draw the Player's shadow dot in the orthogonal view
        self.curr_col = int(x_offset_center + y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET))
        self.curr_row = int((self.player.sprite.shadow_y - MAP_STARTING_POS[1] + (TILE_X_OFFSET*self.curr_layer) )/TILE_Y_OFFSET)
        pg.draw.circle(screen, 'yellow', (x_offset_center*width + 20 + width*y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET), y_offset*height + 20), 2)

    def blit_player_shadow(self):
        curr_jump_height = 1 - (self.player.sprite.shadow_y - self.player.sprite.rect.bottom)/100
        if curr_jump_height <= 0: curr_jump_height = 0

        player_shadow_surf = pg.Surface((PLAYER_SHADOW_WIDTH*curr_jump_height, PLAYER_SHADOW_HEIGHT*curr_jump_height), pg.SRCALPHA)
        pg.draw.ellipse(player_shadow_surf, (0,0,0), player_shadow_surf.get_frect(topleft=(0,0)))
        player_shadow_surf.set_alpha(PLAYER_SHADOW_ALPHA)
        screen.blit(player_shadow_surf, player_shadow_surf.get_frect(center=(self.player.sprite.rect.centerx, self.player.sprite.shadow_y)))
