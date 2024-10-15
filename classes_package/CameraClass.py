import pygame as pg
from pygame.locals import *

import globals
from global_constants import *
from .UsefulFunctions import *


PLAYER_SHADOW_WIDTH = 75
PLAYER_SHADOW_HEIGHT = 30
PLAYER_SHADOW_ALPHA = 100

COLORKEY = (255, 255, 255)

MAP_STARTING_POS = PROJECTION_GROUND_LEVEL_ORIGIN
BIRDS_EYE_SCALE_DOWN_MULT = 3
BIRDS_EYE_STARTING_POS = (20, 20)

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
        self.wait_on = False

    def blit_debug(self):

        if not self.debug: return

        # Show Current Row
        curr_row = int(globals.player.sprite.abstraction_y)
        curr_row_surf = self.font.render(f'Current Row: {int(curr_row)}', None, (255,255,255))
        curr_row_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT))
        screen.blit(curr_row_surf, curr_row_rect)
        # Height of Text
        text_height = curr_row_surf.get_height()

        # Show Current Col
        curr_col = int(globals.player.sprite.abstraction_x)
        curr_col_surf = self.font.render(f'Current Col: {int(curr_col)}', None, (255,255,255))
        curr_col_rect = curr_col_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*1))
        screen.blit(curr_col_surf, curr_col_rect)

        # Show Current Layer
        curr_layer = int(globals.player.sprite.abstraction_h)
        curr_layer_surf = self.font.render(f'Current Layer: {int(curr_layer)}', None, (255,255,255))
        curr_layer_rect = curr_row_surf.get_frect(bottomleft=(0,SCREEN_HEIGHT - text_height*2))
        screen.blit(curr_layer_surf, curr_layer_rect)

    def blit_fps(self):
        fps_surf = self.font.render(f'FPS: {round(clock.get_fps())}', None, (255,255,255))
        screen.blit(fps_surf,(0,0))

    def blit_projection(self):
        # Draw Tiles

        # TODO: separate surfaces for each depth slice

        # Note the drawing order, for purposes of proper occlusion:
        # - draw the background slices before the foreground slices (outermost loop)
        # - within each slice, draw the bottom rows before the top rows (intermediate loop)
        # - within each row, draw left to right (innermost loop) - although this matters the least
        for d in range(globals.map.map_dimensions_depth):
            for h in range(globals.map.map_dimensions_height):
                for w in range(globals.map.map_dimensions_width):

                    x, y, layer = w, d, h
                    tile = globals.map.map_data[layer][y][x]

                    if tile == MAP_EMPTY: continue
                    # if tile in (MAP_EMPTY, 'J', 'L'): continue

                    tile_type = TILE_TYPES[tile]

                    # Highlight the tile the player is on
                    screen.blit(
                        self.highlighted_tiles[tile_type]   if self.show_highlight \
                                                                and globals.player.sprite.abstraction_h == globals.player.sprite.shadow_h \
                                                                and x == int(globals.player.sprite.abstraction_x) \
                                                                and y == int(globals.player.sprite.abstraction_y) \
                                                                and layer == int(globals.player.sprite.abstraction_h) \
                                                            else self.tiles_by_layer[layer][tile_type],
                        self.cube.get_frect(topleft=(
                            MAP_STARTING_POS[0] + x*PROJECTION_TILE_X_OFFSET,
                            MAP_STARTING_POS[1] + y*PROJECTION_TILE_Y_OFFSET - layer*PROJECTION_TILE_Y_OFFSET,
                        ))
                    )

                    # Debug
                    if self.wait_on:
                        pg.time.wait(0)
                        pg.display.update()

                # NOTE: occlusion problem if we draw sprite(s) here, at given d and h:
                # - improper occlusion for F and 7 tiles higher than the sprite's current elevation,
                #   because the sprite is properly drawn AFTER tiles belonging to his current elevation,
                #   but BEFORE tiles belonging to higher elevations. in the case of F and 7, though they are higher,
                #   they should still be behind the overlapping sprite
                # - solution: if you keep redrawing ALL sprites belonging to current d after the h-loop, this works most of the time.
                #   however, you will not get proper occlusion from L and J tiles.

                # if int(globals.player.sprite.abstraction_y) == d and int(globals.player.sprite.abstraction_h) == h:
                #     # print(f'drawing player at d == {d}')
                #     globals.map.blit_player_shadow()
                #     globals.player.draw(screen)

            # Draw Player at correct depth and height
            # TODO: occlusion problem:
            # - improper occlusion for L and J tiles at the sprite's current depth,
            #   because the sprite is properly drawn AFTER tiles belonging to his depth.
            #   however, L and J at current depth should occlude the sprite.
            # - solution: if you only draw sprites in the inner h-loop (i.e. at the correct d and h),
            #   you can ensure that at least higher blocks properly occlude the sprite.
            #   however, F and 7 tiles higher than the sprite, which should be behind the sprite, will improperly occlude him
            # - overall, the better option seems to be drawing sprite within the d-loop, but outside of the h-loop.
            #   the improper L and J non-occlusion is rare and not super noticeable.
            # TODO: don't just draw player. cycle through visible entities list, and organize them by depth
            # in a dict so that for a given d, we can draw all visible entities at that depth
            # TODO: CONSIDER MOVING ALL DRAW FUNCTIONS TO A SEPARATE CLASS


            # if int(globals.player.sprite.abstraction_y) == d:
            # # if int(globals.player.sprite.abstraction_y) == d - 1:
            #     # print(f'drawing player at d == {d}')
            #     globals.map.blit_player_shadow()
            #     globals.player.draw(screen)
            for entity in globals.all_entities:
                if int(entity.sprite.abstraction_y) == d:
                # if int(entity.sprite.abstraction_y) == d - 1:
                    # globals.map.blit_player_shadow()
                    entity.draw(screen)
                    if self.debug: pg.draw.circle(screen, 'green', entity.sprite.shadow_projection, 3)


            for h in range(globals.map.map_dimensions_height):
                for w in range(globals.map.map_dimensions_width):

                    x, y, layer = w, d, h
                    tile = globals.map.map_data[layer][y][x]

                    # if tile == MAP_EMPTY: continue
                    if tile in (MAP_EMPTY, '1', '7', 'F'): continue
                    
                    # if tile in ('J', 'L') and h ..............

                    tile_type = TILE_TYPES[tile]

                    # Highlight the tile the player is on
                    screen.blit(
                        self.highlighted_tiles[tile_type]   if self.show_highlight \
                                                                and globals.player.sprite.abstraction_h == globals.player.sprite.shadow_h \
                                                                and x == int(globals.player.sprite.abstraction_x) \
                                                                and y == int(globals.player.sprite.abstraction_y) \
                                                                and layer == int(globals.player.sprite.abstraction_h) \
                                                            else self.tiles_by_layer[layer][tile_type],
                        self.cube.get_frect(topleft=(
                            MAP_STARTING_POS[0] + x*PROJECTION_TILE_X_OFFSET,
                            MAP_STARTING_POS[1] + y*PROJECTION_TILE_Y_OFFSET - layer*PROJECTION_TILE_Y_OFFSET,
                        ))
                    )

        # # all entities must be sorted by depth (ascending), then height (ascending)
        # for entity in globals.all_entities:
        #     # draw the entity
        #     entity.draw(screen)

        #     # now draw the occluders: iterate through depth, then height, then width
        #     # print(entity.sprite.image.width)

        #     # print(entity.sprite.abstraction_h)
        #     # print(entity.sprite.abstraction_x)
        #     # print(entity.sprite.abstraction_y)
        #     # assert False
        #     # qqq
        #     # self.map_dimensions_height = 0
        #     # self.map_dimensions_width = 0
        #     # self.map_dimensions_depth = 0


        #     width_num_tiles = math.ceil( entity.sprite.image.width / PROJECTION_TILE_X_OFFSET )
        #     height_num_tiles = math.ceil( entity.sprite.image.height / PROJECTION_TILE_Y_OFFSET )
        #     # print(width_num_tiles)
        #     # print(height_num_tiles)
        #     # assert False

        #     int_abstraction_x = int(entity.sprite.abstraction_x)
        #     int_abstraction_y = int(entity.sprite.abstraction_y)
        #     int_abstraction_h = int(entity.sprite.abstraction_h)

        #     for d in range(int_abstraction_y, self.map_dimensions_depth):
        #         delta = d - int_abstraction_y
        #         # for h in range(int_abstraction_h + 1 + delta, self.map_dimensions_height):
        #         for h in range(int_abstraction_h + delta, self.map_dimensions_height):
        #             for w in range(int_abstraction_x - width_num_tiles, int_abstraction_x + width_num_tiles + 1):

        #                 x, y, layer = w, d, h
        #                 if layer >= len(self.map_data): continue
        #                 if y >= len(self.map_data[layer]): continue
        #                 if x >= len(self.map_data[layer][y]): continue
        #                 tile = self.map_data[layer][y][x]

        #                 if tile == MAP_EMPTY: continue
                        
        #                 # if layer < 1: continue

        #                 if tile in ('7', 'F') and h <= int_abstraction_h + 1 + height_num_tiles: continue
        #                 # if tile not in ('J', 'L') and abs(w - int_abstraction_x) <= 1: continue
        #                 # if tile not in ('J', 'L') and abs(w - int_abstraction_x) <= 1 and h <= int_abstraction_h + 1 + height_num_tiles: continue
        #                 if tile not in ('J', 'L') and abs(w - int_abstraction_x) <= 1 and h <= int_abstraction_h + height_num_tiles: continue
        #                 if tile not in ('J', 'L') and h == int_abstraction_h + delta: continue

        #                 # if h == int_abstraction_h + delta and tile not in ('J', 'L'): continue

        #                 tile_type = TILE_TYPES[tile]

        #                 # Highlight the tile the player is on
        #                 screen.blit(
        #                     self.highlighted_tiles[tile_type]   if self.show_highlight \
        #                                                             and globals.player.sprite.abstraction_h == globals.player.sprite.shadow_h \
        #                                                             and x == int(globals.player.sprite.abstraction_x) \
        #                                                             and y == int(globals.player.sprite.abstraction_y) \
        #                                                             and layer == int(globals.player.sprite.abstraction_h) \
        #                                                         else self.tiles_by_layer[layer][tile_type],
        #                     self.cube.get_frect(topleft=(
        #                         MAP_STARTING_POS[0] + x*PROJECTION_TILE_X_OFFSET,
        #                         MAP_STARTING_POS[1] + y*PROJECTION_TILE_Y_OFFSET - layer*PROJECTION_TILE_Y_OFFSET,
        #                     ))
        #                 )

    # TODO: RENAME ALL REFERENCES TO 'BIRDS EYE VIEW' TO SOMETHING LIKE 'ORTHOGONAL ABSTRACTION'
    def draw_birds_eye_view(self):
        x_offset = globals.player.sprite.abstraction_x
        y_offset = globals.player.sprite.abstraction_y

        # These variables are to scale down the tiles to a smaller size
        width = int(self.tile_width/BIRDS_EYE_SCALE_DOWN_MULT)
        height = int(self.tile_height/BIRDS_EYE_SCALE_DOWN_MULT)

        for layer, _ in enumerate(globals.map.map_data):
            for y, row in enumerate(globals.map.map_data[layer]):
                for x, tile in enumerate(row):
                    if tile == MAP_EMPTY: continue

                    TL_corner = (BIRDS_EYE_STARTING_POS[0] + x*width, BIRDS_EYE_STARTING_POS[1] + y*height)
                    TR_corner = (BIRDS_EYE_STARTING_POS[0] + (x+1)*width, BIRDS_EYE_STARTING_POS[1] + y*height)
                    BR_corner = (BIRDS_EYE_STARTING_POS[0] + (x+1)*width, BIRDS_EYE_STARTING_POS[1] + (y+1)*height)
                    BL_corner = (BIRDS_EYE_STARTING_POS[0] + x*width, BIRDS_EYE_STARTING_POS[1] + (y+1)*height)

                    # Topographical heat map; the location of the surf is offsetted just a bit so that it doesn't cover the white outlines
                    heatmap_offset_in_px = 1
                    TL_corner_birdseye = (0 + heatmap_offset_in_px, 0 + heatmap_offset_in_px)
                    TR_corner_birdseye = (width - heatmap_offset_in_px, 0 + heatmap_offset_in_px)
                    BR_corner_birdseye = (width - heatmap_offset_in_px, height - heatmap_offset_in_px)
                    BL_corner_birdseye = (0 + heatmap_offset_in_px, height - heatmap_offset_in_px)

                    heatmap_surf = pg.Surface((width, height))
                    heatmap_surf.set_alpha(50)

                    if tile == MAP_FLOOR:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_birdseye, TR_corner_birdseye, BR_corner_birdseye, BL_corner_birdseye], 0)

                    elif tile == MAP_7:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_birdseye, TR_corner_birdseye, BL_corner_birdseye], 0)

                    elif tile == MAP_F:
                        pg.draw.polygon(screen, 'white', [TL_corner, TR_corner, BR_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_birdseye, TR_corner_birdseye, BR_corner_birdseye], 0)

                    elif tile == MAP_J:
                        pg.draw.polygon(screen, 'white', [TL_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TL_corner_birdseye, BR_corner_birdseye, BL_corner_birdseye], 0)

                    elif tile == MAP_L:
                        pg.draw.polygon(screen, 'white', [TR_corner, BR_corner, BL_corner], 1)
                        pg.draw.polygon(heatmap_surf, 'red', [TR_corner_birdseye, BR_corner_birdseye, BL_corner_birdseye], 0)

                    # Don't draw heatmap for layer 0
                    if layer > 0:
                        screen.blit(heatmap_surf, (BIRDS_EYE_STARTING_POS[0] + x*width, BIRDS_EYE_STARTING_POS[1] + y*height))

        # Draw the Player's width
        player_location = (x_offset*width + BIRDS_EYE_STARTING_POS[0], y_offset*height + BIRDS_EYE_STARTING_POS[1])
        line_length = PLAYER_WIDTH / PROJECTION_TILE_X_OFFSET * width
        left_point = (player_location[0] - line_length/2, player_location[1])
        right_point = (player_location[0] + line_length/2, player_location[1])
        pg.draw.line(screen, 'red', left_point, right_point, 3)

        # Draw the Player's shadow dot
        pg.draw.circle(screen, 'green', (x_offset*width + BIRDS_EYE_STARTING_POS[0], y_offset*height + BIRDS_EYE_STARTING_POS[1]), 2)

    # def blit_player_shadow(self):
    #     curr_jump_height = (globals.player.sprite.abstraction_h - globals.player.sprite.shadow_h) / 10
    #     shadow_multiplier = max(1 - curr_jump_height, 0)
    #     player_shadow_surf = pg.Surface((PLAYER_SHADOW_WIDTH*shadow_multiplier, PLAYER_SHADOW_HEIGHT*shadow_multiplier), pg.SRCALPHA)
    #     pg.draw.ellipse(player_shadow_surf, (0,0,0), player_shadow_surf.get_frect(topleft=(0,0)))
    #     player_shadow_surf.set_alpha(PLAYER_SHADOW_ALPHA)
    #     screen.blit(player_shadow_surf, player_shadow_surf.get_frect(center=projection_coords_by_abstraction_coords(globals.player.sprite.abstraction_x, globals.player.sprite.abstraction_y, globals.player.sprite.shadow_h)))

    def draw(self):
        # screen.fill("black")

        self.blit_debug()
        self.blit_fps()

        self.draw_birds_eye_view()
        self.blit_projection()

        