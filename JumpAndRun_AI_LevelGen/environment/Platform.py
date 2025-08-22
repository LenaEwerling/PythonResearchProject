from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color 
from kivy.core.window import Window
import logging

"""Set up logging."""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Game")

class Platform(Widget):
    """Platform class for the game's ground."""
    def __init__(self, **kwargs):
        """Initialize the platform with size and position."""
        super(Platform, self).__init__(**kwargs)
        self.size = (Window.width, 100)
        self.pos = (0, 0)

        # Draw platform rectangle
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1) # gray
            self.rect = Rectangle(pos=self.pos, size=self.size)