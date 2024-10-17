import pygame as pg
from pygame.locals import *
from global_constants import *
from .UsefulFunctions import *
import globals

import json

file_map = 'ortho_map.txt'

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

        # TODO: SUPER TEMPORARY CODE
        self.enemy_locations = []

        # Read map file
        temp_map_data = {}
        f = open(file_map)
        for block_idx, block_str in enumerate(f.read().split('\n\n')):
            [ block_label, *block_data ] = block_str.split('\n')

            if 'LAYER' in block_label:
                layer_num = int(block_label.split(' ')[1])
                # # TODO: REMOVE?
                # if layer_num == 0: continue
                self.map_dimensions_height = max(self.map_dimensions_height, layer_num + 1)

                curr_layer = block_idx
                temp_map_data[curr_layer] = []
                for row in block_data:
                    temp_map_data[curr_layer].append([c for c in row])
                    self.map_dimensions_width = max(self.map_dimensions_width, len(row))
                self.map_dimensions_depth = max(self.map_dimensions_depth, len(block_data))
            elif 'ENTITIES' in block_label:
                for line in block_data:
                    data = json.loads(line)
                    # print(data)
                    match data['Entity']:
                        case 'Player':
                            self.player_start_x, self.player_start_y, self.player_start_h = data['x'], data['y'], data['h']
                        case 'Enemy':

                            # TODO: SUPER TEMPORARY CODE
                            self.enemy_locations.append({ 'x': data['x'], 'y': data['y'], 'h': data['h'] })
                            
                            # pass
                        
        f.close()
        for layer in range(self.map_dimensions_height):
            if layer in temp_map_data:
                self.map_data.append(temp_map_data[layer])
            else:
                self.map_data.append([ [MAP_EMPTY] * self.map_dimensions_width for _ in range(self.map_dimensions_depth) ])

    def on_globals_loaded(self):
        pass

    def update(self):
        pass