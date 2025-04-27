import random
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color 
from kivy.core.window import Window

class Obstacle(Widget):

    obstacle_kind_count = 2

    def __init__(self, obstacle_type, speed, **kwargs):
        super(Obstacle, self).__init__(**kwargs)
        self.speed = speed #speed from left to right
        self.pos = [Window.width, 100] # starts on the right
        self.counted = False #tracks whether the obstacle was counted for stats

        #Types of Obstacles
        type_index = random.randrange(0,2) if obstacle_type is None else obstacle_type
        match type_index:
            case 0:  
                self.size = (40, 60) # low Rectange
                self.type = "low_block"
            case 1:
                self.size = (40, 100) # high Rectangle
                self.type = "high_block"
            case _:
                raise ValueError(f"Invalid obstacle_type: {type_index}")

        #draw obstacle
        with self.canvas:
            Color(0,1,0,1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def update(self):
        #move obstacle to left
        self.pos[0] += self.speed
        self.rect.pos = self.pos