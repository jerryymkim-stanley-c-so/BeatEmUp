import pygame as pg
from pygame.locals import *
from global_constants import *
from .UsefulFunctions import *
import globals

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

class Map():
    def __init__(self):

        # Init attributes
        self.map_data = []
        self.map_dimensions_height = 0
        self.map_dimensions_width = 0
        self.map_dimensions_depth = 0
        self.player_start_x = 0
        self.player_start_y = 0
        self.player_start_h = 0

        # Read map file
        temp_map_data = {}
        f = open(file_map)
        for block_idx, block_str in enumerate(f.read().split('\n\n')):
            [ block_label, *block_data ] = block_str.split('\n')

            if 'LAYER' in block_label:
                layer_num = int(block_label.split(' ')[1])
                self.map_dimensions_height = max(self.map_dimensions_height, layer_num + 1)

                curr_layer = block_idx
                temp_map_data[curr_layer] = []
                for row in block_data:
                    temp_map_data[curr_layer].append([c for c in row])
                    self.map_dimensions_width = max(self.map_dimensions_width, len(row))
                self.map_dimensions_depth = max(self.map_dimensions_depth, len(block_data))
            elif 'DATA' in block_label:
                for line in block_data:
                    [ line_label, line_data ] = line.split(': ')
                    match line_label:
                        case 'Player Start':
                            self.player_start_x, self.player_start_y, self.player_start_h = ( float(n) for n in line_data.split(', ') )
        f.close()
        for layer in range(self.map_dimensions_height):
            if layer in temp_map_data:
                self.map_data.append(temp_map_data[layer])
            else:
                self.map_data.append([ [MAP_EMPTY] * self.map_dimensions_width for _ in range(self.map_dimensions_depth) ])

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
        rgb_multiplier = 256 // self.map_dimensions_height

        for i in range(self.map_dimensions_height):
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
        self.font = pg.font.Font(None, 25)
        self.show_highlight = False
        self.wait_on = False

    def on_globals_loaded(self):
        pass


    def blit_debug(self):

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

    def blit_map(self):
        # Draw Tiles

        # TODO: separate surfaces for each depth slice

        # Note the drawing order, for purposes of proper occlusion:
        # - draw the background slices before the foreground slices (outermost loop)
        # - within each slice, draw the bottom rows before the top rows (intermediate loop)
        # - within each row, draw left to right (innermost loop) - although this matters the least
        for d in range(self.map_dimensions_depth):
            for h in range(self.map_dimensions_height):
                for w in range(self.map_dimensions_width):

                    x, y, layer = w, d, h
                    tile = self.map_data[layer][y][x]

                    if tile == MAP_EMPTY: continue

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

            if int(globals.player.sprite.abstraction_y) == d:
                # print(f'drawing player at d == {d}')
                globals.map.blit_player_shadow()
                globals.player.draw(screen)


    # TODO: RENAME ALL REFERENCES TO 'BIRDS EYE VIEW' TO SOMETHING LIKE 'ORTHOGONAL ABSTRACTION'
    def draw_birds_eye_view(self):
        x_offset = globals.player.sprite.abstraction_x
        y_offset = globals.player.sprite.abstraction_y

        # These variables are to scale down the tiles to a smaller size
        width = int(self.tile_width/BIRDS_EYE_SCALE_DOWN_MULT)
        height = int(self.tile_height/BIRDS_EYE_SCALE_DOWN_MULT)

        for layer, _ in enumerate(self.map_data):
            for y, row in enumerate(self.map_data[layer]):
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

    def blit_player_shadow(self):
        curr_jump_height = (globals.player.sprite.abstraction_h - globals.player.sprite.shadow_h) / 10
        shadow_multiplier = max(1 - curr_jump_height, 0)
        player_shadow_surf = pg.Surface((PLAYER_SHADOW_WIDTH*shadow_multiplier, PLAYER_SHADOW_HEIGHT*shadow_multiplier), pg.SRCALPHA)
        pg.draw.ellipse(player_shadow_surf, (0,0,0), player_shadow_surf.get_frect(topleft=(0,0)))
        player_shadow_surf.set_alpha(PLAYER_SHADOW_ALPHA)
        screen.blit(player_shadow_surf, player_shadow_surf.get_frect(center=projection_coords_by_abstraction_coords(globals.player.sprite.abstraction_x, globals.player.sprite.abstraction_y, globals.player.sprite.shadow_h)))

    def update(self):
        pass