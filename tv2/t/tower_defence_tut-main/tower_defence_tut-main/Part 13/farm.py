import pygame as pg
import constants as c
from farm_data import FARM_DATA

class Farm(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y):
        pg.sprite.Sprite.__init__(self)
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

    def update(self, game):
        # Generate money at intervals
        if pg.time.get_ticks() - self.last_generation > c.GENERATION_INTERVAL:
            game.add_money(self.money_generated)
            self.last_generation = pg.time.get_ticks()

    def upgrade(self):
        self.upgrade_level += 1
        self.money_generated = FARM_DATA[self.upgrade_level - 1].get("money_generated")

    def draw(self, surface):
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)

    def __init__(self, money_per_interval=10, interval=1000):
        self.money_per_interval = money_per_interval
        self.interval = interval
        self.last_money_generated_time = pg.time.get_ticks()

    def update(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_money_generated_time >= self.interval:
            self.generate_money()
            self.last_money_generated_time = current_time

    def generate_money(self):
        self.money += self.money_per_interval
        print(f"Money generated: {self.money_per_interval}. Total money: {self.money}")

    def get_money(self):
        return self.money