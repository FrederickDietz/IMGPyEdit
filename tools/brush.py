import pygame
from PIL import ImageDraw

class Tool:
    def handle_event(self, event, image, color):
        """Draw on the PIL Image using mouse events."""
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
            # Get the state of the mouse buttons
            buttons = pygame.mouse.get_pressed()
            if buttons[0]:  # Left mouse button pressed
                x, y = pygame.mouse.get_pos()
                x, y = x, y - 50  # Adjust for canvas position
                if 0 <= x < image.width and 0 <= y < image.height:
                    draw = ImageDraw.Draw(image)
                    draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=color)
