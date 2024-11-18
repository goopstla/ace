import pygame as pg
import constants as c
from farm_data import FARM_DATA

class Farm(pg.sprite.Sprite):
    def __init__(self, tile_x, tile_y, money_per_interval=10, interval=1000):
        super().__init__()  # Call the Sprite constructor
        self.upgrade_level = 1
        self.money_generated = FARM_DATA[self.upgrade_level - 1].get("money_generated")
        self.last_generation = pg.time.get_ticks()
        self.selected = False

        # Position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        # Calculate center coordinates
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        
        # Money generation attributes
        self.money_per_interval = money_per_interval
        self.interval = interval
        self.last_money_generated_time = pg.time.get_ticks()
        self.money = 0  # Initialize money attribute

        # Load the farm image (make sure the path is correct)
        self.image = pg.image.load('assets/images/turrets/idk.png').convert_alpha()  # Adjust the path as needed
        
        # Scale the image and assign it back to self.image
        self.image = pg.transform.scale(self.image, (65, 65))  # Resize the image to 65x65 pixels
        self.rect = self.image.get_rect(center=(self.x, self.y))  # Set the rect position

    def update(self, game):
        # Generate money at intervals
        current_time = pg.time.get_ticks()
        if current_time - self.last_generation > c.GENERATION_INTERVAL:
            game.add_money(self.money_generated)
            self.last_generation = current_time
        
        # Handle money generation
        if current_time - self.last_money_generated_time >= self.interval:
            self.generate_money()
            self.last_money_generated_time = current_time

    def upgrade(self):
        self.upgrade_level += 1
        self.money_generated = FARM_DATA[self.upgrade_level - 1].get("money_generated")

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def generate_money(self):
        self.money += self.money_per_interval
        print(f"Money generated: {self.money_per_interval}. Total money: {self.money}")

    def get_money(self):
        return self.money