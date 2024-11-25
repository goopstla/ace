import pygame as pg
import RPi.GPIO as GPIO
import time
import neopixel
import json
import time
from enemy import Enemy
from world import World
from turret import Turret
from turret2 import Turret2
from button import Button
import constants as c
from farm import Farm
from menu import Menu

#step motor setup
#gpio setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

#define sequence for stepper motor
step_sequence = [
[1,0,0,0],
[1,1,0,0],
[0,1,0,0],
[0,1,1,0],
[0,0,1,0],
[1,0,1,1],
[0,0,0,1],
[1,0,0,1],
] 
def step_motor(delay,steps):
    for _ in range(steps):
        for step in step_sequence:
            GPIO.output(17, step[0])
            GPIO.output(18, step[0])
            GPIO.output(27, step[0])
            GPIO.output(22, step[0])
try:
    delay=0.005 #adjust to make it faster
    steps= 512 # one revo is 512 steps
    while True:
        step_motor(delay,steps) #continuous spin
except KeyboardInterrupt:
    ()
finally:
  GPIO.cleanup()

# Setup NeoPixel
neopixel_main = neopixel.NeoPixel(board.D21, 50, brightness=1)

lightpin = 21

# Define colors for each area
colors = [
    (150, 0, 0),     # Red
    (0, 150, 0),     # Green
    (0, 0, 150),     # Blue
    (150, 150, 0),   # Yellow
    (0, 150, 150),   # Cyan
    (150, 0, 150),   # Magenta
    (150, 150, 150), # White
    (150, 50, 0),    # Orange
    (150, 0, 0),     # Red for remaining areas
    (150, 0, 0),
    (150, 0, 0),
    (150, 0, 0),
    (150, 0, 0),
    (150, 0, 0)
]

# Define which LEDs correspond to each area
led_areas = {
   1: range(0, 50),
}

# Function to set LED colors based on areas
def light_up_areas():
    for area, leds in led_areas.items():
        color = colors[area - 1]
        for led_index in leds:
            neopixel_main[led_index] = color
    neopixel_main.show()  # Update the LED strip
    time.sleep(1)  # Delay for effect

# Function to clear all LEDs
def cleanup_leds():
    neopixel_main.fill((0, 0, 0))
    neopixel_main.show()

# Run the function to light up LEDs
try:
    light_up_areas()
finally:
    cleanup_leds()  # Turn off LEDs when done

#initialise pygame
pg.init() 

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

# Load the main menu
menu = Menu()

# Run the main menu
# Load the main menu
menu = Menu()

# Run the main menu
menu.run(screen)
#game variables
game_over = False
game_outcome = 0 # -1 is loss & 1 is win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
placing_turrets2 = False
placing_farm = False
selected_turret = None
selected_turret2 = None
selected_farm = None

#load images
#map
map_image = pg.image.load('levels/level.png').convert_alpha()
#individual turret image for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/ribosome.png').convert_alpha()
cursor_turret = pg.transform.scale(cursor_turret, (50, 50))
# cursor turret2
cursor_turret2 = pg.image.load('assets/images/turrets/nucleoid.png').convert_alpha()
cursor_turret2 = pg.transform.scale(cursor_turret2, (50, 50))
#individual turret image for mouse cursor
cursor_farm = pg.image.load('assets/images/turrets/plasmid.png').convert_alpha()
cursor_farm = pg.transform.scale(cursor_farm, (50, 50))

#enemies
image_size = (64, 64)  # Example size, adjust as needed

enemy_images = {
    "weak": pg.transform.scale(pg.image.load('assets/images/enemies/idk.png').convert_alpha(), image_size),
    "medium": pg.transform.scale(pg.image.load('assets/images/enemies/idk.png').convert_alpha(), image_size),
    "strong": pg.transform.scale(pg.image.load('assets/images/enemies/idk.png').convert_alpha(), image_size),
    "elite": pg.transform.scale(pg.image.load('assets/images/enemies/idk.png').convert_alpha(), image_size)
}
#buttons
buy_turret_image = pg.image.load('assets/images/turrets/ribosome_moneyover.png').convert_alpha()
buy_turret_image = pg.transform.scale(buy_turret_image, (50, 50))
buy_turret2_image = pg.image.load('assets/images/turrets/nucleoid_moneyover.png').convert_alpha()
buy_turret2_image = pg.transform.scale(buy_turret2_image, (50, 50))
buy_farm_image = pg.image.load('assets/images/turrets/plasmid_moneyover.png').convert_alpha()
buy_farm_image = pg.transform.scale(buy_farm_image, (50, 50))
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
#gui
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()

#load sounds
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(1)

#load json data for level
with open('levels/level.tmj') as file:
  world_data = json.load(file)

#load fonts for displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def display_data():
  #draw panel
  pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #display data
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
  draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
  draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)
  
# turret creation
def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calculate the sequential number of the tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if that tile is grass
  if world.tile_map[mouse_tile_num] == 20: 
    #check that there isn't already a turret there
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    #if it is a free space then create turret
    if space_is_free == True:
      new_turret = Turret(mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group.add(new_turret)
      #deduct cost of turret
      world.money -= c.BUY_COST
      # Light up the NeoPixel strip in blue
      light_up_strip((0, 0, 150))  # Blue color
  
def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      # Light up the NeoPixel strip in blue
      light_up_strip((0, 0, 150))  # Blue color
      return turret

# turret2 creation
def create_turret2(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calculate the sequential number of the tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if that tile is grass
  if world.tile_map[mouse_tile_num] == 20:
    #check that there isn't already a turret there
    space_is_free = True
    for turret2 in turret_group2:
      if (mouse_tile_x, mouse_tile_y) == (turret2.tile_x, turret2.tile_y):
        space_is_free = False
    #if it is a free space then create turret
    if space_is_free == True:
      new_turret2 = Turret2(mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group2.add(new_turret2)
      #deduct cost of turret
      world.money -= c.BUY_COST2
      # Light up the NeoPixel strip in brown
    light_up_strip((139, 69, 19))  # Brown color
  
def select_turret2(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret2 in turret_group2:
    if (mouse_tile_x, mouse_tile_y) == (turret2.tile_x, turret2.tile_y):
      # Light up the NeoPixel strip in brown
      light_up_strip((139, 69, 19))  # Brown color
      return turret2


# create farm 
def create_farm(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calculate the sequential number of the tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if that tile is grass
  if world.tile_map[mouse_tile_num] == 7:
    #check that there isn't already a farm there
    space_is_free = True
    for farm in farm_group:
      if (mouse_tile_x, mouse_tile_y) == (farm.tile_x, farm.tile_y):
        space_is_free = False
    #if it is a free space then create turret
    if space_is_free == True:
      new_farm = Farm(mouse_tile_x, mouse_tile_y)
      farm_group.add(new_farm)
      #deduct cost of turret
      world.money -= c.FARM_COST
      # Light up the NeoPixel strip in purple
      light_up_strip((128, 0, 128))  # Purple color

def select_farm(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for farm in farm_group:
        if (mouse_tile_x, mouse_tile_y) == (farm.tile_x, farm.tile_y):
          # Light up the NeoPixel strip in purple
            light_up_strip((128, 0, 128))  # Purple color
            return farm

def clear_selection():
  for turret in turret_group:
    turret.selected = False
  for turret2 in turret_group2:
    turret2.selected = False

#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

# Initialize previous_health after world is created
previous_health = world.health

# Function to light up the entire NeoPixel strip in a specific color
def light_up_strip(color):
    for i in range(neopixel_main.n):
        neopixel_main[i] = color  # Set each LED to the specified color
    neopixel_main.show()  # Update the strip

# Function to clear all LEDs
def cleanup_leds():
    neopixel_main.fill((0, 0, 0))
    neopixel_main.show()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()
turret_group2 = pg.sprite.Group()
farm_group = pg.sprite.Group()

waypoints = [
  (2, 337),
  (144, 336),
  (145, 146),
  (335, 144),
  (337, 479),
  (528, 481),
  (529, 289),
  (718, 289)
]

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 40, 135, buy_turret_image, True)
turret2_button = Button(c.SCREEN_WIDTH + 100, 135, buy_turret2_image, True)
farm_button = Button(c.SCREEN_WIDTH + 160, 135, buy_farm_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 200, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

#game loop
run = True
while run:
  clock.tick(c.FPS)

  #########################
  # UPDATING SECTION
  #########################

  if game_over == False:
    #check if player has lost
    if world.health <= 0:
      game_over = True
      game_outcome = -1 #loss
    if world.health < previous_health:  # Check if health has decreased
            light_up_strip((150, 0, 0))  # Light up the strip in red
            time.sleep(1)  # Keep it red for a second
            cleanup_leds()  # Clear the LEDs after a moment
    #check if player has won
    elif world.level > c.TOTAL_LEVELS:
      game_over = True
      game_outcome = 1 #win

        # Update previous health
      previous_health = world.health

    #update groups
    enemy_group.update(world)
    turret_group.update(enemy_group, world)
    turret_group2.update(enemy_group, world)
    farm_group.update(world)

    #highlight selected turret
    if selected_turret:
      selected_turret.selected = True

    # highlight turret2 
    if selected_turret2:
      selected_turret2.selected = True
    
     # highlight farm
    if selected_farm:
      selected_farm.selected = True

  #########################
  # DRAWING SECTION
  #########################

  #draw level
  world.draw(screen)
  
  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

  for turret2 in turret_group2:
    turret2.draw(screen)
  
  for farm in farm_group:
    farm.draw(screen)

  display_data()

  if game_over == False:
    #check if the level has been started or not
    if level_started == False:
      if begin_button.draw(screen):
        level_started = True
    else:
      #fast forward option
      world.game_speed = 1
      if fast_forward_button.draw(screen):
        world.game_speed = 2
      #spawn enemies
      if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
        if world.spawned_enemies < len(world.enemy_list):
          enemy_type = world.enemy_list[world.spawned_enemies]
          enemy = Enemy(enemy_type, waypoints, enemy_images)
          enemy_group.add(enemy)
          world.spawned_enemies += 1
          last_enemy_spawn = pg.time.get_ticks()

    #check if the wave is finished
    if world.check_level_complete() == True:
      world.money += c.LEVEL_COMPLETE_REWARD
      world.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      world.reset_level()
      world.process_enemies()

    #draw buttons
    #button for placing turrets
    #for the "turret button" show cost of turret and draw the button
    if turret_button.draw(screen):
      placing_turrets = not placing_turrets

    if turret2_button.draw(screen):
      placing_turrets2 = not placing_turrets2     

    if farm_button.draw(screen):
      placing_farm = not placing_farm

    #if placing turrets then show the cancel button as well

    # placing turrets when you press buy
    if placing_turrets:
      cursor_rect = cursor_turret.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_turret, cursor_rect)

     # placing turrets2   
    if placing_turrets2:
      cursor_rect = cursor_turret2.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_turret2, cursor_rect)        
        
    # placing farm when buy pressed
    if placing_farm:
      cursor_rect = cursor_farm.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        screen.blit(cursor_farm, cursor_rect)

    #if a turret is selected then show the upgrade button
    if selected_turret:
      #if a turret can be upgraded then show the upgrade button
      if selected_turret.upgrade_level < c.TURRET_LEVELS:
        #show cost of upgrade and draw the button
        draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST:
            selected_turret.upgrade()
            world.money -= c.UPGRADE_COST
      # turret2 selected show upgrade
    if selected_turret2:
      #if a turret can be upgraded then show the upgrade button
      if selected_turret2.upgrade_level < c.TURRET_LEVELS:
        #show cost of upgrade and draw the button
        draw_text(str(c.UPGRADE_COST2), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST2:
            selected_turret2.upgrade()
            world.money -= c.UPGRADE_COST2

        #if a farm is selected then show the upgrade button
    if selected_farm:
      selected_farm.selected = True
      #if a turret can be upgraded then show the upgrade button
      if selected_farm.upgrade_level < c.FARM_LEVELS:
        #show cost of upgrade and draw the button
        draw_text(str(c.FARMUPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST:
            selected_farm.upgrade()
            world.money -= c.FARMUPGRADE_COST
  else:
    pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius = 30)
    if game_outcome == -1:
      draw_text("GAME OVER", large_font, "grey0", 310, 230)
    elif game_outcome == 1:
      draw_text("YOU WIN!", large_font, "grey0", 315, 230)
    #restart level
    if restart_button.draw(screen):
      game_over = False
      level_started = False
      placing_turrets = False
      placing_farm = False
      selected_turret = None
      selected_farm = None
      last_enemy_spawn = pg.time.get_ticks()
      world = World(world_data, map_image)
      world.process_data()
      world.process_enemies()
      #empty groups
      enemy_group.empty()
      turret_group.empty()

  #event handler
  for event in pg.event.get():
    #quit program
    if event.type == pg.QUIT:
      run = False
    #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if mouse is on the game area
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        #clear selected turrets
        selected_turret = None
        selected_turret2 = None
        clear_selection()
        if placing_turrets == True:
          #check if there is enough money for a turret
          if world.money >= c.BUY_COST:
            create_turret(mouse_pos)
        if placing_turrets2 == True:
          #check if there is enough money for a turret
          if world.money >= c.BUY_COST2:
            create_turret2(mouse_pos)         
        elif placing_farm == True:
          #check if there is enough money for a farm
          if world.money >= c.FARM_COST:
            create_farm(mouse_pos)    
        else:
          selected_turret = select_turret(mouse_pos)
          selected_turret2 = select_turret2(mouse_pos)
          selected_farm = select_farm(mouse_pos)

  #update display
  pg.display.flip()

pg.quit()