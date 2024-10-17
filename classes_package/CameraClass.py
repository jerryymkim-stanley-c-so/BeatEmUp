import pygame as pg
from pygame.locals import *

import globals
from global_constants import *
from .UsefulFunctions import *


PLAYER_SHADOW_WIDTH = 75
PLAYER_SHADOW_HEIGHT = 30
PLAYER_SHADOW_ALPHA = 100

COLORKEY = (255, 255, 255)

ABSTRACTION_MINIMAP_SCALE_DOWN_MULT = 3
ABSTRACTION_MINIMAP_STARTING_POS = (20, 20)

file_map = 'ortho_map.txt'
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

class Camera():
    def __init__(self):
        pass

    def on_globals_loaded(self):
        
        # Init tiles
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
        self.tile_height = self.tile_width # the height, for purposes of this variable, is equal to the width, because the floor portion of the tile is like a square. (the true height of the image includes the thickness of the tile)

        # Create tileset of progressively lighter colors based on layer level
        def create_color_swapped_tile_from_template(template, old_floor_color, new_floor_color, old_wall_color, new_wall_color):
            tile = template.copy()
            pixels = pg.PixelArray(tile)
            pixels.replace(pg.Color(*old_floor_color), pg.Color(*new_floor_color))
            pixels.replace(pg.Color(*old_wall_color), pg.Color(*new_wall_color))
            return tile

        self.tiles_by_layer = []
        rgb_multiplier = 256 // globals.map.map_dimensions_height

        for i in range(globals.map.map_dimensions_height):
            rgb_shift = rgb_multiplier * (i+1) - 1
            self.tiles_by_layer.append({
                cube: create_color_swapped_tile_from_template(self.cube, GENERIC_FLOOR_COLOR, (0, 0, rgb_shift), GENERIC_WALL_COLOR, (rgb_shift, rgb_shift, rgb_shift)),
                half_7: create_color_swapped_tile_from_template(self.half_7, GENERIC_FLOOR_COLOR, (0, 0, rgb_shift), GENERIC_WALL_COLOR, (rgb_shift, rgb_shift, rgb_shift)),
                half_F: create_color_swapped_tile_from_template(self.half_F, GENERIC_FLOOR_COLOR, (0, 0, rgb_shift), GENERIC_WALL_COLOR, (rgb_shift, rgb_shift, rgb_shift)),
                half_J: create_color_swapped_tile_from_template(self.half_J, GENERIC_FLOOR_COLOR, (0, 0, rgb_shift), GENERIC_WALL_COLOR, (rgb_shift, rgb_shift, rgb_shift)),
                half_L: create_color_swapped_tile_from_template(self.half_L, GENERIC_FLOOR_COLOR, (0, 0, rgb_shift), GENERIC_WALL_COLOR, (rgb_shift, rgb_shift, rgb_shift)),
            })

        self.highlighted_tiles = {
            cube: create_color_swapped_tile_from_template(self.cube, GENERIC_FLOOR_COLOR, YELLOW, GENERIC_WALL_COLOR, ALMOST_WHITE),
            half_7: create_color_swapped_tile_from_template(self.half_7, GENERIC_FLOOR_COLOR, YELLOW, GENERIC_WALL_COLOR, ALMOST_WHITE),
            half_F: create_color_swapped_tile_from_template(self.half_F, GENERIC_FLOOR_COLOR, YELLOW, GENERIC_WALL_COLOR, ALMOST_WHITE),
            half_J: create_color_swapped_tile_from_template(self.half_J, GENERIC_FLOOR_COLOR, YELLOW, GENERIC_WALL_COLOR, ALMOST_WHITE),
            half_L: create_color_swapped_tile_from_template(self.half_L, GENERIC_FLOOR_COLOR, YELLOW, GENERIC_WALL_COLOR, ALMOST_WHITE),
        }

        # Debug Variables
        self.debug = True
        self.font = pg.font.Font(None, 25)
        self.show_highlight = False
        self.show_highlight = True

    def draw_debug(self):

        if not self.debug: return

        # Show Current Row
        curr_row = int(globals.player.abstraction_y)
        curr_row_surf = self.font.render(f'Current Row: {int(curr_row)}', None, (255,255,255))
        curr_row_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT))
        screen.blit(curr_row_surf, curr_row_rect)
        # Height of Text
        text_height = curr_row_surf.get_height()

        # Show Current Col
        curr_col = int(globals.player.abstraction_x)
        curr_col_surf = self.font.render(f'Current Col: {int(curr_col)}', None, (255,255,255))
        curr_col_rect = curr_col_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*1))
        screen.blit(curr_col_surf, curr_col_rect)

        # Show Current Layer
        curr_layer = int(globals.player.abstraction_h)
        curr_layer_surf = self.font.render(f'Current Layer: {int(curr_layer)}', None, (255,255,255))
        curr_layer_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*2))
        screen.blit(curr_layer_surf, curr_layer_rect)

    def draw_fps(self):
        fps_surf = self.font.render(f'FPS: {round(clock.get_fps())}', None, (255,255,255))
        screen.blit(fps_surf,(0,0))

    def draw_projection(self):

        # Prepare all sprite locations
        sprites_by_pos = {}
        for sprite in globals.all_sprites:
            int_abstraction_y = int(sprite.abstraction_y)
            int_abstraction_h = int(sprite.abstraction_h)
            coord = (int_abstraction_y, int_abstraction_h)
            if sprite == globals.player:
                print(f'PLAYER | {coord}')
            if coord not in sprites_by_pos: sprites_by_pos[coord] = []
            sprites_by_pos[coord].append(sprite)

            # Within each list, sort by y value so that sprites with higher values of y are drawn later
            for lst in sprites_by_pos.values():
                lst.sort(key=lambda sprite: sprite.abstraction_y)

        # For each depth slice...
        for d in range(globals.map.map_dimensions_depth):

            # ...Draw all '1', '7', 'F' tiles belonging to the entire depth slice
            for h in range(globals.map.map_dimensions_height):
                for w in range(globals.map.map_dimensions_width):

                    x, y, layer = w, d, h
                    tile = globals.map.map_data[layer][y][x]

                    if tile not in (MAP_EMPTY, 'J', 'L'):

                        tile_type = TILE_TYPES[tile]

                        # Highlight the tile the player is on
                        screen.blit(
                            self.highlighted_tiles[tile_type]   if self.show_highlight \
                                                                    and globals.player.abstraction_h == globals.player.shadow_h \
                                                                    and x == int(globals.player.abstraction_x) \
                                                                    and y == int(globals.player.abstraction_y) \
                                                                    and layer == int(globals.player.abstraction_h) \
                                                                else self.tiles_by_layer[layer][tile_type],
                            self.cube.get_frect(topleft=projection_coords_by_abstraction_coords(x, y, layer))
                        )

            # Then go height layer by layer, and for each height...
            EXTRA_BUFFER_FOR_JUMPING_FROM_HIGHEST_LEVEL = 2
            for h in range(globals.map.map_dimensions_height + EXTRA_BUFFER_FOR_JUMPING_FROM_HIGHEST_LEVEL):
                y, layer = d, h

                # ...Draw remaining tile types first
                if h < globals.map.map_dimensions_height:
                    for w in range(globals.map.map_dimensions_width):
                        x = w
                        tile = globals.map.map_data[layer][y][x]

                        if tile not in (MAP_EMPTY, '1', '7', 'F'):

                            tile_type = TILE_TYPES[tile]

                            # Highlight the tile the player is on
                            screen.blit(
                                self.highlighted_tiles[tile_type]   if self.show_highlight \
                                                                        and globals.player.abstraction_h == globals.player.shadow_h \
                                                                        and x == int(globals.player.abstraction_x) \
                                                                        and y == int(globals.player.abstraction_y) \
                                                                        and layer == int(globals.player.abstraction_h) \
                                                                    else self.tiles_by_layer[layer][tile_type],
                                self.cube.get_frect(topleft=projection_coords_by_abstraction_coords(x, y, layer))
                            )

                # ...Then draw sprites at current depth slice and height layer
                if (y, layer) in sprites_by_pos:
                    for sprite in sprites_by_pos[(y, layer)]:
                        # TODO: SET DYNAMIC OFFSET
                        offset = pg.Vector2()
                        offset.x = 0
                        offset.y = 0
                        screen.blit(sprite.image, sprite.rect.topleft + offset)
                        if self.debug: pg.draw.circle(screen, 'green', sprite.shadow_projection, 3)


    def draw_abstraction_minimap(self):
        x_offset = globals.player.abstraction_x
        y_offset = globals.player.abstraction_y

        # These variables are to scale down the tiles to a smaller size
        width = int(self.tile_width/ABSTRACTION_MINIMAP_SCALE_DOWN_MULT)
        height = int(self.tile_height/ABSTRACTION_MINIMAP_SCALE_DOWN_MULT)

        for layer, _ in enumerate(globals.map.map_data):
            for y, row in enumerate(globals.map.map_data[layer]):
                for x, tile in enumerate(row):
                    if tile == MAP_EMPTY: continue

                    TL_corner = (ABSTRACTION_MINIMAP_STARTING_POS[0] + x*width, ABSTRACTION_MINIMAP_STARTING_POS[1] + y*height)
                    TR_corner = (ABSTRACTION_MINIMAP_STARTING_POS[0] + (x+1)*width, ABSTRACTION_MINIMAP_STARTING_POS[1] + y*height)
                    BR_corner = (ABSTRACTION_MINIMAP_STARTING_POS[0] + (x+1)*width, ABSTRACTION_MINIMAP_STARTING_POS[1] + (y+1)*height)
                    BL_corner = (ABSTRACTION_MINIMAP_STARTING_POS[0] + x*width, ABSTRACTION_MINIMAP_STARTING_POS[1] + (y+1)*height)

                    # Topographical heat map; the location of the surf is offsetted just a bit so that it doesn't cover the white outlines
                    heatmap_offset_in_px = 1
                    TL_corner_abstraction = (0 + heatmap_offset_in_px, 0 + heatmap_offset_in_px)
                    TR_corner_abstraction = (width - heatmap_offset_in_px, 0 + heatmap_offset_in_px)
                    BR_corner_abstraction = (width - heatmap_offset_in_px, height - heatmap_offset_in_px)
                    BL_corner_abstraction = (0 + heatmap_offset_in_px, height - heatmap_offset_in_px)

                    heatmap_surf = pg.Surface((width, height))
                    heatmap_surf.set_alpha(50)

                    if tile == MAP_FLOOR:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_abstraction, TR_corner_abstraction, BR_corner_abstraction, BL_corner_abstraction], 0)

                    elif tile == MAP_7:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_abstraction, TR_corner_abstraction, BL_corner_abstraction], 0)

                    elif tile == MAP_F:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BR_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_abstraction, TR_corner_abstraction, BR_corner_abstraction], 0)

                    elif tile == MAP_J:
                        pg.draw.polygon(screen, 'white', [TL_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_abstraction, BR_corner_abstraction, BL_corner_abstraction], 0)

                    elif tile == MAP_L:
                        pg.draw.polygon(screen, 'white', [TR_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TR_corner_abstraction, BR_corner_abstraction, BL_corner_abstraction], 0)

                    # Don't draw heatmap for layer 0
                    if layer > 0:
                        screen.blit(heatmap_surf, (ABSTRACTION_MINIMAP_STARTING_POS[0] + x*width, ABSTRACTION_MINIMAP_STARTING_POS[1] + y*height))

        # Draw the Player's width
        player_location = (x_offset*width + ABSTRACTION_MINIMAP_STARTING_POS[0], y_offset*height + ABSTRACTION_MINIMAP_STARTING_POS[1])
        line_length = PLAYER_WIDTH / PROJECTION_TILE_X_OFFSET * width
        left_point = (player_location[0] - line_length/2, player_location[1])
        right_point = (player_location[0] + line_length/2, player_location[1])
        pg.draw.line(screen, 'red', left_point, right_point, 3)

        # Draw the Player's shadow dot
        pg.draw.circle(screen, 'green', (x_offset*width + ABSTRACTION_MINIMAP_STARTING_POS[0], y_offset*height + ABSTRACTION_MINIMAP_STARTING_POS[1]), 2)

    # def blit_player_shadow(self):
    #     curr_jump_height = (globals.player.abstraction_h - globals.player.shadow_h) / 10
    #     shadow_multiplier = max(1 - curr_jump_height, 0)
    #     player_shadow_surf = pg.Surface((PLAYER_SHADOW_WIDTH*shadow_multiplier, PLAYER_SHADOW_HEIGHT*shadow_multiplier), pg.SRCALPHA)
    #     pg.draw.ellipse(player_shadow_surf, (0,0,0), player_shadow_surf.get_frect(topleft=(0,0)))
    #     player_shadow_surf.set_alpha(PLAYER_SHADOW_ALPHA)
    #     screen.blit(player_shadow_surf, player_shadow_surf.get_frect(center=projection_coords_by_abstraction_coords(globals.player.abstraction_x, globals.player.abstraction_y, globals.player.shadow_h)))

    def draw(self):

        self.draw_debug()
        self.draw_fps()

        self.draw_abstraction_minimap()
        self.draw_projection()
        