import pygame as pg
import random
import constants as c
from enemy_data import ENEMY_SPAWN_DATA

class World():
  def __init__(self, data, map_image):
    self.level = 1
    self.game_speed = 1
    self.health = c.HEALTH
    self.money = c.MONEY
    self.tile_map = []
    self.level_data = data
    self.image = map_image
    self.enemy_list = []
    self.spawned_enemies = 0
    self.killed_enemies = 0
    self.missed_enemies = 0

  def process_data(self):
    #look through data to extract relevant info
    for layer in self.level_data["layers"]:
      if layer["name"] == "tilemap":
        self.tile_map = layer["data"]
        
  def process_enemies(self):
    enemies = ENEMY_SPAWN_DATA[self.level - 1]
    for enemy_type in enemies:
      enemies_to_spawn = enemies[enemy_type]
      for enemy in range(enemies_to_spawn):
        self.enemy_list.append(enemy_type)
    #now randomize the list to shuffle the enemies
    random.shuffle(self.enemy_list)

  def check_level_complete(self):
    if (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
      return True

  def reset_level(self):
    #reset enemy variables
    self.enemy_list = []
    self.spawned_enemies = 0
    self.killed_enemies = 0
    self.missed_enemies = 0

  def draw(self, surface):
    surface.blit(self.image, (0, 0))