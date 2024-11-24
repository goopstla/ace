import pygame as pg
import math
import constants as c
from turret2_data import TURRET2_DATA

class Turret2(pg.sprite.Sprite):
    def __init__(self, tile_x, tile_y, shot_fx):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.range = TURRET2_DATA[self.upgrade_level - 1].get("range") 
        self.cooldown = TURRET2_DATA[self.upgrade_level - 1].get("cooldown")
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None

        # Initialize the angle
        self.angle = 90  # Default angle

        # Position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        # Calculate center coordinates
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        # Shot sound effect
        self.shot_fx = shot_fx

        # Load and transform image
        self.image = pg.image.load('assets/images/turrets/nucleoid.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (100, 100))
        self.original_image = self.image  # Keep a reference to the original image
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Create transparent circle showing range
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

    def update(self, enemy_group, world):
        # Search for new target once turret has cooled down
        if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
            self.pick_target(enemy_group)

    def pick_target(self, enemy_group):
        # Find an enemy to target
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))  # Update angle based on target
                    # Damage enemy
                    self.target.health -= c.DAMAGE2
                    # Play sound effect
                    self.shot_fx.play()
                    self.last_shot = pg.time.get_ticks()  # Reset last shot time
                    break

    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRET2_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET2_DATA[self.upgrade_level - 1].get("cooldown")

        # Upgrade range circle
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect(center=self.rect.center)

    def draw(self, surface):
        # Rotate the turret image based on the angle
        rotated_image = pg.transform.rotate(self.original_image, -self.angle + 90)  # Adjust for correct orientation
        self.rect = rotated_image.get_rect(center=(self.x, self.y))  # Update the rect to the new rotated image
        surface.blit(rotated_image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)