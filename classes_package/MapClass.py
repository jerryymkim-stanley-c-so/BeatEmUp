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

COLORKEY = (255, 255, 255)

MAP_STARTING_POS = (600, 340)
# TILE_X_OFFSET = 76
# TILE_Y_OFFSET = 30
MAP_STARTING_POS = (0, 0)
TILE_X_OFFSET = 50
TILE_Y_OFFSET = 50
TILE_ELEVATION_Y_OFFSET = 76
BIRDS_EYE_SCALE_DOWN_MULT = 5


# file_map = 'map.txt'
# file_cube = 'graphics/cube_testblock.png'
# file_cube_highlight = 'graphics/cube_highlighted_testblock.png'
file_map = 'ortho_map.txt'
# file_map = 'ortho_map2.txt'
file_cube = 'graphics/ortho_cube.png'
file_half_7 = 'graphics/ortho_half_7.png'
file_half_F = 'graphics/ortho_half_F.png'
file_half_J = 'graphics/ortho_half_J.png'
file_half_L = 'graphics/ortho_half_L.png'

GENERIC_FLOOR_COLOR = (153, 217, 234)
GENERIC_WALL_COLOR = (195, 195, 195)
ALMOST_WHITE = (254, 254, 254)
YELLOW = (255, 242, 0)

TILE_TYPES = {
    "1": cube,
    "7": half_7,
    "F": half_F,
    "J": half_J,
    "L": half_L,
}

class Map():
    def __init__(self):
        self.player = globals.player

        self.map_data = {}
        self.map_dimensions_height = 0
        self.map_dimensions_width = 0
        self.map_dimensions_depth = 0

        # def create_map_data():
        #     map_data = {}

        #     f = open(file_map)

        #     # curr_layer = None
        #     # for row in f.read().split('\n'):
        #     #     if 'Layer' in row:
        #     #         curr_layer = row
        #     #         map_data[curr_layer] = []
        #     #     elif row:
        #     #         # map_data[curr_layer].append([int(c) for c in row])
        #     #         map_data[curr_layer].append([c for c in row])

        #     # Alternate method of reading, By Stan
        #     for layer_str in f.read().split('\n\n'):
        #         layer = layer_str.split('\n')
        #         curr_layer = layer[0]
        #         map_data[curr_layer] = []
        #         for i in range(1, len(layer)):
        #             row = layer[i]
        #             map_data[curr_layer].append([c for c in row])

        #     f.close()
        #     return map_data
        # self.map_data = create_map_data()

        f = open(file_map)
        curr_layer = 0
        for layer_str in f.read().split('\n\n'):
            layer = layer_str.split('\n')
            # curr_layer = layer[0]
            self.map_data[curr_layer] = []
            for i in range(1, len(layer)):
                row = layer[i]
                self.map_data[curr_layer].append([c for c in row])
                self.map_dimensions_width = max(self.map_dimensions_width, len(row))
            
            self.map_dimensions_depth = max(self.map_dimensions_depth, len(layer) - 1)
            self.map_dimensions_height += 1
            curr_layer += 1
        f.close()

        # Print map_data
        # for key in self.map_data.keys():
        #     for row in self.map_data[key]:
        #         print(f'{key}: {row}')
        # print(self.map_data)
        # print(self.map_dimensions_height)
        # print(self.map_dimensions_width)
        # print(self.map_dimensions_depth)


        self.cube = pg.image.load(file_cube).convert_alpha()
        self.cube.set_colorkey(COLORKEY)
        self.half_7 = pg.image.load(file_half_7).convert_alpha()
        self.half_7.set_colorkey(COLORKEY)
        self.half_F = pg.image.load(file_half_F).convert_alpha()
        self.half_F.set_colorkey(COLORKEY)
        self.half_J = pg.image.load(file_half_J).convert_alpha()
        self.half_J.set_colorkey(COLORKEY)
        self.half_L = pg.image.load(file_half_L).convert_alpha()
        self.half_L.set_colorkey(COLORKEY)

        self.tile_width = self.cube.get_width()
        self.tile_height = self.cube.get_height()

        self.tiles = []
        rgb_multiplier = 256 // self.map_dimensions_height
        # print(rgb_multiplier)
        for i in range(self.map_dimensions_height):
            
            tile_cube = self.cube.copy()
            tile_half_7 = self.half_7.copy()
            tile_half_F = self.half_F.copy()
            tile_half_J = self.half_J.copy()
            tile_half_L = self.half_L.copy()

            for tile in [
                tile_cube,
                tile_half_7,
                tile_half_F,
                tile_half_J,
                tile_half_L,
            ]:
                pixels = pg.PixelArray(tile)
                pixels.replace(pg.Color(*GENERIC_FLOOR_COLOR), pg.Color(0, 0, rgb_multiplier * (i+1) - 1))
                pixels.replace(pg.Color(*GENERIC_WALL_COLOR), pg.Color(rgb_multiplier * (i+1) - 1, rgb_multiplier * (i+1) - 1, rgb_multiplier * (i+1) - 1))

            # self.tiles.append(cube)
            self.tiles.append({
                cube: tile_cube,
                half_7: tile_half_7,
                half_F: tile_half_F,
                half_J: tile_half_J,
                half_L: tile_half_L,
            })

        tile_highlighted_cube = self.cube.copy()
        tile_highlighted_half_7 = self.half_7.copy()
        tile_highlighted_half_F = self.half_F.copy()
        tile_highlighted_half_J = self.half_J.copy()
        tile_highlighted_half_L = self.half_L.copy()

        for tile in [
            tile_highlighted_cube,
            tile_highlighted_half_7,
            tile_highlighted_half_F,
            tile_highlighted_half_J,
            tile_highlighted_half_L,
        ]:
            pixels = pg.PixelArray(tile)
            pixels.replace(pg.Color(*GENERIC_FLOOR_COLOR), pg.Color(*YELLOW))
            pixels.replace(pg.Color(*GENERIC_WALL_COLOR), pg.Color(*ALMOST_WHITE))

        self.highlighted_tiles = {
            cube: tile_highlighted_cube,
            half_7: tile_highlighted_half_7,
            half_F: tile_highlighted_half_F,
            half_J: tile_highlighted_half_J,
            half_L: tile_highlighted_half_L,
        }

        self.font = pg.font.Font(None, 25)

        # Debug Variables
        # self.curr_layer = 0
        self.curr_layer = 1
        self.curr_row = 0
        self.curr_col = 0
        self.wait_on = False
        # self.wait_on = True

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

        # for layer, key in enumerate(self.map_data.keys()):
        #     for y, row in enumerate(self.map_data[key]):
        #         for x, tile in enumerate(row):

        for d in range(self.map_dimensions_depth):
            y = d
            # for h in range(self.map_dimensions_height):
            for h in range(self.map_dimensions_height - 1, -1, -1):
                layer = self.map_dimensions_height - 1 - h
                for w in range(self.map_dimensions_width):
                    x = w

                    tile = self.map_data[self.map_dimensions_height - 1 - h][d][w]

                    # if not tile: continue
                    if tile == '.': continue

                    tile_type = TILE_TYPES[tile]

                    rect = self.cube.get_frect(topleft=(
                        # MAP_STARTING_POS[0] + x*TILE_X_OFFSET - y*TILE_Y_OFFSET,
                        # MAP_STARTING_POS[1] + y*TILE_Y_OFFSET - layer*TILE_X_OFFSET
                        MAP_STARTING_POS[0] + x*TILE_X_OFFSET,
                        MAP_STARTING_POS[1] + y*TILE_Y_OFFSET - layer*TILE_Y_OFFSET,
                    ))

                    # Highlight the tile the player is on
                    screen.blit(
                        # self.highlight_cube if rect.collidepoint(midbottom) and rect.top <= bottom <= rect.top + 32 else self.cube,
                        # self.highlight_cube if rect.collidepoint(midbottom) and rect.top <= bottom <= rect.top + self.tile_width else self.tiles[layer],
                        self.highlighted_tiles[tile_type] if rect.collidepoint(midbottom) and rect.top <= bottom <= rect.top + self.tile_width and self.curr_layer == layer else self.tiles[layer][tile_type],
                        rect
                    )

                    if self.wait_on:
                        # pg.time.wait(200)
                        pg.time.wait(0)
                        pg.display.update()

                    # # Draw Player at the correct time
                    # if self.curr_row == y and self.curr_col == x:
                    # # if True:
                    #     # globals.map.blit_player_shadow()
                    #     globals.player.draw(screen)

            # Draw Player at the correct time
            # if self.curr_row == y and self.curr_col == x:
            if self.curr_row == d:
            # if True:
                # globals.map.blit_player_shadow()
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

    # def blit_player_shadow(self):
    #     curr_jump_height = 1 - (self.player.sprite.shadow_y - self.player.sprite.rect.bottom)/100
    #     if curr_jump_height <= 0: curr_jump_height = 0

    #     player_shadow_surf = pg.Surface((PLAYER_SHADOW_WIDTH*curr_jump_height, PLAYER_SHADOW_HEIGHT*curr_jump_height), pg.SRCALPHA)
    #     pg.draw.ellipse(player_shadow_surf, (0,0,0), player_shadow_surf.get_frect(topleft=(0,0)))
    #     player_shadow_surf.set_alpha(PLAYER_SHADOW_ALPHA)
    #     screen.blit(player_shadow_surf, player_shadow_surf.get_frect(center=(self.player.sprite.rect.centerx, self.player.sprite.shadow_y)))


    def update(self):
        # Offset is subtracted by TILE_Y_OFFSET because of the shift in the topleft corner of rhombus
        # Since it's 45 degrees, TILE_Y_OFFSET would be the same as making an 'X' offset by just that triangle's amount
        # Everything is divided by TILE_X_OFFSET to enumerate which tile the player is on
        # For example, if the player is on the 0th tile in the x-direction, the x_offset should be somewhere between 0.00 -- 1.00
        # The same logic applies for the y_offset, however the 'self.curr_layer*TILE_X_OFFSET' accounts for how high the player is in elevation
        x_offset_center = (self.player.sprite.rect.centerx - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        # x_offset_left = (self.player.sprite.rect.left - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        # x_offset_right = (self.player.sprite.rect.right - MAP_STARTING_POS[0] - TILE_Y_OFFSET)/TILE_X_OFFSET
        y_offset = (self.player.sprite.shadow_y - MAP_STARTING_POS[1] + self.curr_layer*TILE_X_OFFSET)/TILE_Y_OFFSET

        # These variables are to scale down the tiles to a smaller size
        width = self.tile_width/BIRDS_EYE_SCALE_DOWN_MULT
        height = self.tile_height/BIRDS_EYE_SCALE_DOWN_MULT

        # self.curr_col = int(x_offset_center + y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET))
        self.curr_col = int(x_offset_center)
        self.curr_row = int((self.player.sprite.shadow_y - MAP_STARTING_POS[1] + (TILE_X_OFFSET*self.curr_layer) )/TILE_Y_OFFSET)
        pg.draw.circle(screen, 'yellow', (x_offset_center*width + 20 + width*y_offset*(TILE_Y_OFFSET/TILE_X_OFFSET), y_offset*height + 20), 2)