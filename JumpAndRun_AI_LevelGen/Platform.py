from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color 
from kivy.core.window import Window

class Platform(Widget):
    def __init__(self, **kwargs):
        super(Platform, self).__init__(**kwargs)
        self.size = (Window.width, 100)
        self.pos = (0, 0)

        #paint platform
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1) #gray
            self.rect = Rectangle(pos=self.pos, size=self.size)