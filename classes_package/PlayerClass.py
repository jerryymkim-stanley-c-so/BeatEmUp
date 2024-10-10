import pygame as pg
from pygame.locals import *

import globals
from global_constants import *
from .UsefulFunctions import *
# from .MapClass import Map


PLAYER_SIZE = (PLAYER_WIDTH, PLAYER_HEIGHT)
PLAYER_MVMT_X_SPD = 5
PLAYER_MVMT_Y_SPD = 3
PLAYER_JUMP_SPD = 16
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
        self.rect = self.image.get_frect(center=(0,0))

        self.is_jumping = False
        self.vertical_speed = 0
        self.horizontal_speed = 0
        self.depth_speed = 0
        self.shadow_h = 0
        self.shadow_projection = (0, 0)

    def on_globals_loaded(self):
        
        # Reposition the player at the start location
        self.abstraction_x = globals.map.player_start_x
        self.abstraction_y = globals.map.player_start_y
        self.abstraction_h = globals.map.player_start_h

    def apply_x_movement(self):
        proposed_x = self.abstraction_x + self.horizontal_speed * self.dt

        # NOTE: we check self.abstraction_h + 1 because the collision checking function CEILS the given h and checks the voxel BELOW it.
        # thus if we are standing at (on top of) some h, potential collision would be with a voxel that lives in layer (h + 1).
        if point_collides_with_terrain(proposed_x, self.abstraction_y, math.floor(self.abstraction_h + 1), globals.map) == False:
            self.abstraction_x = proposed_x

        self.horizontal_speed = 0

    def apply_y_movement(self):
        proposed_y = self.abstraction_y + self.depth_speed * self.dt

        # NOTE: we check self.abstraction_h + 1 because the collision checking function CEILS the given h and checks the voxel BELOW it.
        # thus if we are standing at (on top of) some h, potential collision would be with a voxel that lives in layer (h + 1).
        if point_collides_with_terrain(self.abstraction_x, proposed_y, math.floor(self.abstraction_h + 1), globals.map) == False:
            self.abstraction_y = proposed_y

        self.depth_speed = 0

    def apply_h_movement(self):
        
        # Always apply displacement due to vertical speed. We will subsequently compare with shadow_h for corrections.
        self.abstraction_h += self.vertical_speed * self.dt

        # If abstraction_h is greater than shadow_h, we are airborne
        if self.abstraction_h > self.shadow_h:
            self.vertical_speed += PLAYER_GRAVITY_RATE

        # If abstraction_h is less than shadow_h, we have landed (and are colliding with the ground), so apply fixes
        if self.abstraction_h < self.shadow_h:
            self.abstraction_h = self.shadow_h
            self.is_jumping = False
            self.vertical_speed = 0

        # TODO: Add code to check for head collisions. This is not going to be common.
        # The only reason we don't do something similar for floor collisions here is because of the concept of the shadow dot,
        # although the shadow dot itself is constantly doing a scan down.
        # - Is it worth keeping the shadow dot?
        # - Should there be an upward analog to the shadow dot for ceiling collisions?
        # - Basically, should we be consistent about floor/ceiling collisions?
        # - Or should we just ignore ceiling collisions altogether, as it likely wouldn't ever come up in a level?

    # TODO: THINK ABOUT WHETHER INPUTS BELONG IN A SEPARATE CLASS?
    # - yes: cleanly separating the keyboard from the player specifically may be beneficial down the line,
    #        especially if the keyboard affects other things beyond just the player
    # - no: the player controlled character differs inherently from similar classes (like NPCs) in that the player controls him,
    #       so it might make sense to integrate control with the playable character
    def resolve_input(self):
        keys = pg.key.get_pressed()

        # Movement
        if keys[K_a] \
            and (self.abstraction_h == self.shadow_h or self.is_jumping):  # allow for directional control when grounded or mid-jump, but not when falling
            self.horizontal_speed = -PLAYER_MVMT_X_SPD
            
        if keys[K_d] \
            and (self.abstraction_h == self.shadow_h or self.is_jumping):
            self.horizontal_speed = PLAYER_MVMT_X_SPD

        if keys[K_w] \
            and (self.abstraction_h == self.shadow_h or self.is_jumping):
            self.depth_speed = -PLAYER_MVMT_Y_SPD

        if keys[K_s] \
            and (self.abstraction_h == self.shadow_h or self.is_jumping):
            self.depth_speed = PLAYER_MVMT_Y_SPD

        if keys[K_SPACE] and self.abstraction_h == self.shadow_h:
            self.is_jumping = True
            self.vertical_speed = PLAYER_JUMP_SPD


    def update_sprite_position(self):
        
        # The sprite is inherently tied to the projection, but the projection follows the abstraction.
        # So, the sprite should reposition itself based on the abstraction.
        self.rect.center = projection_coords_by_abstraction_coords(self.abstraction_x, self.abstraction_y, self.abstraction_h)
        self.rect.y -= PLAYER_HEIGHT // 2


    def update_shadow(self):

        # Constantly scan down from current position to update shadow dot elevation
        self.shadow_h = min(int(self.abstraction_h), globals.map.map_dimensions_height - 1)  # shadow cannot exceed highest map layer

        while 0 <= (self.shadow_h - 1) < len(globals.map.map_data) \
            and point_collides_with_terrain(self.abstraction_x, self.abstraction_y, self.shadow_h, globals.map) == False:
            self.shadow_h -= 1

        # Draw green dot at shadow
        self.shadow_projection = projection_coords_by_abstraction_coords(self.abstraction_x, self.abstraction_y, self.shadow_h)
        # TODO: it doesn't seem ideal for most classes to be concerned with drawing to the screen. should something else be handling the drawing?
        pg.draw.circle(screen, 'green', self.shadow_projection, 3)

    def update_dt(self):
        self.dt = globals.dt

    def update(self):
        self.update_dt()
        self.update_shadow()

        # TODO: DOES THE ORDER OF AXIS RESOLUTION MATTER? COULD THERE BE ANY WEIRD EDGE CASES THAT LEAD TO STRANGE BEHAVIOR?
        self.apply_x_movement()
        self.apply_y_movement()
        self.apply_h_movement()

        self.update_sprite_position()

        # Resolve inputs
        self.resolve_input()
