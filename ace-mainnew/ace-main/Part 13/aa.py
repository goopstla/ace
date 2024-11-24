import pygame
import sys

# Initialize pygame
pygame.init()

# Define constants
ROWS = 15
COLS = 15
TILE_SIZE = 48
SIDE_PANEL = 300
SCREEN_WIDTH = TILE_SIZE * COLS + SIDE_PANEL  # Add the side panel width to the screen
SCREEN_HEIGHT = TILE_SIZE * ROWS
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Waypoint Clicker')

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Waypoints list
waypoints = []

# Load the background image (make sure the path is correct)
background_image = pygame.image.load("levels/level.png")
background_image = pygame.transform.scale(background_image, (TILE_SIZE * COLS, TILE_SIZE * ROWS))  # Resize to the grid size

# Font for displaying text (for waypoint coordinates)
font = pygame.font.Font(None, 36)

def draw_waypoints():
    """Draw the waypoints on the screen"""
    for waypoint in waypoints:
        # Draw a red circle at each waypoint
        pygame.draw.circle(screen, RED, waypoint, 5)
        # Draw the coordinates next to each waypoint
        text = font.render(f'({waypoint[0]}, {waypoint[1]})', True, RED)
        screen.blit(text, (waypoint[0] + 10, waypoint[1] - 10))

def draw_side_panel():
    """Draw the blank side panel"""
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - SIDE_PANEL, 0, SIDE_PANEL, SCREEN_HEIGHT))  # Side panel background

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Capture mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()  # Get mouse position
                waypoints.append(mouse_pos)  # Add the waypoint to the list
                print(f"Waypoint clicked at: {mouse_pos}")  # Print the waypoint to the console
    
    # Fill the screen with white
    screen.fill(WHITE)
    
    # Draw the background image (the map), excluding the side panel area
    screen.blit(background_image, (0, 0))
    
    # Draw waypoints on top of the background
    draw_waypoints()
    
    # Draw the side panel (empty)
    draw_side_panel()
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
