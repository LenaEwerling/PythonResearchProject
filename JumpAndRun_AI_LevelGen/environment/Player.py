from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color 
import logging

"""Set up logging."""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Game")

class Player(Widget):
    """Player class for handling player movement and graphics."""
    def __init__(self, **kwargs):
        """Initialize the player with size, position, and physics."""
        super(Player, self).__init__(**kwargs)
        self.size = (50,50)
        self.size_hint = (None, None)
        self.pos = (100, 100)
        self.velocity_y = 0
        self.gravity = -0.3
        self.jump_strength = 8.5
        self.is_jumping = False
        self.max_jumps = 2

        # Draw player rectangle
        with self.canvas:
            Color(1, 0, 0, 1) # red
            self.rect = Rectangle(pos=self.pos, size=self.size)
    
    def update(self):
        """Update player position based on velocity and gravity."""
        # Apply gravity
        self.velocity_y += self.gravity
        self.pos[1] += self.velocity_y

        jump_height = 0

        # Check contact with ground
        if self.pos[1] <= 100: # ground height
            self.pos[1] = 100
            jump_height = self.is_jumping
            self.velocity_y = 0
            self.is_jumping = 0

        # Update rectangle position
        self.rect.pos = self.pos
        return jump_height

    def jump(self):
        """Handle player jump if jumps are available."""
        if self.is_jumping < self.max_jumps:
            self.velocity_y = self.jump_strength
            self.is_jumping += 1

    def reset(self):
        """Reset player to initial state."""
        self.size = (50,50)
        self.pos = (100, 100)
        self.is_jumping = False
        self.velocity_y = 0
        logger.info(f"reset Player: {self.pos}, jumping: {self.is_jumping}, velocity:{self.velocity_y}")