import pygame
import sys
import importlib
import os
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT = 300, 300
CANVAS_WIDTH, CANVAS_HEIGHT = 300, 300
TOOL_DIR = "tools"
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Variables ---
current_tool = None
available_tools = {}
selected_color = GREEN
canvas_resolution = [DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT]  # Mutable for input
layers = [{"visible": True, "image": Image.new("RGBA", (DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT), (0, 0, 0, 0)), "name": "Layer 1"}]
resolution_input = ["300", "300"]
current_input_box = 0
active_layer_index = 0  # Index of the active layer

# Initialize Pygame Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Interactive Modular Drawing Program")
clock = pygame.time.Clock()


# --- Functions ---
def load_tools():
    """Dynamically load tools from the tools directory."""
    global available_tools
    available_tools.clear()

    if not os.path.exists(TOOL_DIR):
        os.makedirs(TOOL_DIR)

    for file in os.listdir(TOOL_DIR):
        if file.endswith(".py") and file != "__init__.py":
            tool_name = file[:-3]
            module = importlib.import_module(f"{TOOL_DIR}.{tool_name}")
            available_tools[tool_name] = module.Tool()
    print("Available Tools: ", list(available_tools.keys()))


def input_color():
    """Prompt the user to input RGBA values."""
    try:
        r = int(input("Enter Red value (0-255): ").strip())
        g = int(input("Enter Green value (0-255): ").strip())
        b = int(input("Enter Blue value (0-255): ").strip())
        a = int(input("Enter Alpha value (0-255): ").strip())
        return (r, g, b, a)
    except ValueError:
        print("Invalid input! Using default color.")
        return GREEN


def add_layer():
    """Add a new blank transparent layer."""
    layer_name = f"Layer {len(layers) + 1}"
    layers.append({"visible": True, "image": Image.new("RGBA", tuple(canvas_resolution), (0, 0, 0, 0)), "name": layer_name})
    print(f"New layer added: {layer_name}")


def delete_layer(index):
    """Delete the layer at the given index."""
    if len(layers) > 1:  # Prevent deleting all layers
        del layers[index]
        print(f"Layer {index + 1} deleted.")
    else:
        print("Cannot delete the last remaining layer.")


def input_resolution():
    """Prompt the user to input new resolution."""
    try:
        new_width = int(input("Enter new width: ").strip())
        new_height = int(input("Enter new height: ").strip())
        return [str(new_width), str(new_height)]
    except ValueError:
        print("Invalid resolution input! Using default resolution.")
        return [str(DEFAULT_CANVAS_WIDTH), str(DEFAULT_CANVAS_HEIGHT)]


def set_resolution():
    """Set the new canvas resolution and resize layers."""
    global layers, canvas_resolution, resolution_input
    try:
        new_width = int(resolution_input[0])
        new_height = int(resolution_input[1])
        new_resolution = (new_width, new_height)

        # Update the global canvas resolution
        canvas_resolution = new_resolution
        
        
        # Resize all layers to match the new resolution
        for layer in layers:
            resized_image = layer["image"].resize(new_resolution, Image.Resampling.LANCZOS)
            layer["image"] = resized_image
        print(f"Resolution set to {new_width}x{new_height}")
    except ValueError:
        print("Invalid resolution input! Using default resolution.")

        

def select_tool():
    """Prompt the user to select a tool by typing its name."""
    global current_tool
    print("\nAvailable Tools:")
    for tool in available_tools.keys():
        print(f"- {tool}")
    tool_id = input("Type the tool name to select it: ").strip()
    if tool_id in available_tools:
        current_tool = available_tools[tool_id]
        print(f"Tool '{tool_id}' selected.")
    else:
        print("Invalid tool name!")


def draw_gui():
    """Draw GUI components."""
    # File Menu
    pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, 50))
    font = pygame.font.Font(None, 30)
    screen.blit(font.render("File: open | new | save", True, BLACK), (10, 10))

    # Tools Button
    pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH + 20, 70, 150, 40))
    screen.blit(font.render("Tools", True, BLACK), (CANVAS_WIDTH + 70, 80))

    # Color Palette
    pygame.draw.rect(screen, selected_color, (CANVAS_WIDTH + 20, 150, 50, 50))
    screen.blit(font.render("Color", True, BLACK), (CANVAS_WIDTH + 90, 165))

    # Resolution Input
    screen.blit(font.render("Resolution:", True, BLACK), (CANVAS_WIDTH + 20, 250))
    pygame.draw.rect(screen, WHITE, (CANVAS_WIDTH + 20, 280, 60, 30))
    pygame.draw.rect(screen, WHITE, (CANVAS_WIDTH + 90, 280, 60, 30))
    screen.blit(font.render(resolution_input[0], True, BLACK), (CANVAS_WIDTH + 30, 285))
    screen.blit(font.render(resolution_input[1], True, BLACK), (CANVAS_WIDTH + 100, 285))
    pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH + 160, 280, 80, 30))
    screen.blit(font.render("Set", True, BLACK), (CANVAS_WIDTH + 180, 285))

    # Add Layer Button
    pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH + 20, 330, 150, 40))
    screen.blit(font.render("Add Layer", True, BLACK), (CANVAS_WIDTH + 35, 340))

    # Layers
    layer_y = 400
    for i, layer in enumerate(layers):
        # Toggle visibility
        color = BLACK if layer["visible"] else GRAY
        pygame.draw.rect(screen, WHITE, (CANVAS_WIDTH + 20, layer_y, 150, 30))
        screen.blit(font.render(f"Layer {i + 1}: {'on' if layer['visible'] else 'off'}", True, color),
                    (CANVAS_WIDTH + 30, layer_y + 5))

        # Delete button (left side of the layer)
        pygame.draw.rect(screen, RED, (CANVAS_WIDTH + 180, layer_y, 50, 30))
        screen.blit(font.render("Del", True, WHITE), (CANVAS_WIDTH + 190, layer_y + 5))

        # Highlight active layer
        if i == active_layer_index:
            pygame.draw.rect(screen, GREEN, (CANVAS_WIDTH + 20, layer_y, 150, 30), 2)

        layer_y += 40

    # Active Layer Name Input
    active_layer = layers[active_layer_index]
    pygame.draw.rect(screen, WHITE, (CANVAS_WIDTH + 20, layer_y, 200, 30))
    screen.blit(font.render(f"Active Layer: {active_layer['name']}", True, BLACK), (CANVAS_WIDTH + 20, layer_y + 5))


def handle_events():
    """Handle all user events."""
    global selected_color, resolution_input, current_input_box, current_tool, active_layer_index
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Color box click
            if CANVAS_WIDTH + 20 < mouse_x < CANVAS_WIDTH + 70 and 150 < mouse_y < 200:
                selected_color = input_color()

            # Set resolution (Prompt user for input when button is clicked)
            elif CANVAS_WIDTH + 160 < mouse_x < CANVAS_WIDTH + 240 and 280 < mouse_y < 310:
                resolution_input = input_resolution()  # Ask for resolution input from the user
                set_resolution()
                
            # Tools button click
            elif CANVAS_WIDTH + 20 < mouse_x < CANVAS_WIDTH + 170 and 70 < mouse_y < 110:
                if available_tools:
                    select_tool()  # Prompt tool selection from the console

            # Add layer
            elif CANVAS_WIDTH + 20 < mouse_x < CANVAS_WIDTH + 170 and 330 < mouse_y < 370:
                add_layer()

            # Layers toggle or delete
            layer_y = 400
            for i, layer in enumerate(layers):
                if CANVAS_WIDTH + 20 < mouse_x < CANVAS_WIDTH + 170 and layer_y < mouse_y < layer_y + 30:
                    layer["visible"] = not layer["visible"]
                elif CANVAS_WIDTH + 180 < mouse_x < CANVAS_WIDTH + 230 and layer_y < mouse_y < layer_y + 30:
                    delete_layer(i)
                layer_y += 40

        if event.type == pygame.KEYDOWN:
            # Switch active layer with arrow keys
            if event.key == pygame.K_DOWN:
                active_layer_index = (active_layer_index + 1) % len(layers)
            elif event.key == pygame.K_UP:
                active_layer_index = (active_layer_index - 1) % len(layers)
                
            if event.key == pygame.K_BACKSPACE:
                layers[active_layer_index]["name"] = layers[active_layer_index]["name"][:-1]
            elif event.key == pygame.K_RETURN:
                # Enter key confirms the name change
                pass
            else:
                layers[active_layer_index]["name"] += event.unicode

        # Ensure the current tool handles events
        if current_tool:
            current_tool.handle_event(event, layers[active_layer_index]["image"], selected_color)



def draw_canvas():
    """Draw the canvas with layers."""
    # Create a surface with the updated canvas resolution
    canvas_surface = pygame.Surface(canvas_resolution)

    # Draw each layer (if visible) onto the canvas surface
    for layer in layers:
        if layer["visible"]:
            pygame_image = pygame.image.fromstring(layer["image"].tobytes(), layer["image"].size, "RGBA")
            canvas_surface.blit(pygame_image, (0, 0))

    # Scale the canvas to fit the original display size (if necessary)
    scaled_canvas = pygame.transform.scale(canvas_surface, (DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT))
    screen.blit(scaled_canvas, (0, 50))



def main():
    load_tools()
    
    # Automatically select the 'brush' tool if available
    global current_tool
    if 'brush' in available_tools:
        current_tool = available_tools['brush']
        print("Brush tool selected automatically.")
    else:
        print("Brush tool not found. Please ensure it's in the 'tools' directory.")
    
    # Initialize the selected tool (if needed)
    if current_tool:
        # Initialize the tool if it has an init method or other necessary setup
        if hasattr(current_tool, "initialize"):
            current_tool.initialize()

    while True:
        handle_events()
        screen.fill(WHITE)
        draw_gui()
        draw_canvas()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
