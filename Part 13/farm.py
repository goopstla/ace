import pygame as pg
import constants as c
from world import World
from farm_data import FARM_DATA

class Farm(pg.sprite.Sprite):
    def __init__(self, tile_x, tile_y, money_per_interval=100):
        super().__init__()  # Call the Sprite constructor
        self.upgrade_level = 1
        self.cooldown = FARM_DATA[self.upgrade_level - 1].get("cooldown")
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
        self.last_money_generated_time = pg.time.get_ticks()
        self.money = 0  # money attribute

        # Load the farm image (make sure the path is correct)
        self.image = pg.image.load('assets/images/turrets/plasmid.png').convert_alpha()  # Adjust the path as needed
        self.image = pg.transform.scale(self.image, (400, 400))
        
        # Scale the image and assign it back to self.image
        self.image = pg.transform.scale(self.image, (30, 30))  # Resize the image to 65x65 pixels
        self.rect = self.image.get_rect(center=(self.x, self.y))  # Set the rect position

    def update(self, game):
        # Handle money generation based on cooldown
        current_time = pg.time.get_ticks()
        if current_time - self.last_money_generated_time >= self.cooldown:
            self.generate_money(game)  # Pass the game/world instance
            self.last_money_generated_time = current_time

    def upgrade(self):
        if self.upgrade_level < len(FARM_DATA):  # Ensure we don't exceed the available upgrades
            self.upgrade_level += 1
            self.cooldown = FARM_DATA[self.upgrade_level - 1].get("cooldown")  # Update cooldown based on new level

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def generate_money(self, world):
        world.money += self.money_per_interval  # Increment the world money
        print(f"Money generated: {self.money_per_interval}. Total money: {world.money}")
        
        # Assuming you want to add the generated money to the game world
        # You may need to adjust this according to your game's architecture
        # For example, if you have a method in the game world to add money:
        # game.add_money(self.money_per_interval)

    def get_money(self):
        return self.money