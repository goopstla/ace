import pygame as pg
from button import Button
import constants as c

class Menu:
    def __init__(self):
        # Load the background image
        self.background = pg.image.load('menu/menu.png').convert_alpha()
        self.background = pg.transform.scale(self.background, (c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))

        # Load and resize the play button image
        play_button_image = pg.image.load('menu/start.png').convert_alpha()
        play_button_image = pg.transform.scale(play_button_image, (230, 180))  # Resize

        # Create the play button at specific coordinates
        self.play_button = Button(400, 470,
            play_button_image, True)

    def draw(self, screen):
        # Draw the background
        screen.blit(self.background, (0, 0))
        # Draw the play button
        if self.play_button.draw(screen):
            return True  # Indicate that the button was clicked
        return False  # Indicate that the button was not clicked

    def run(self, screen):
        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

            # Draw the menu and check for button click
            if self.draw(screen):
                run = False  # Exit the menu loop to start the game

            # Update the display
            pg.display.flip()