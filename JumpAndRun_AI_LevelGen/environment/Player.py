from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color 

class Player(Widget):
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.size = (50,50)
        self.pos = (100, 100)
        self.velocity_y = 0
        self.gravity = -0.3
        self.jump_strength = 8.5
        self.is_jumping = False
        self.max_jumps = 2

        # draw player
        with self.canvas:
            Color(1, 0, 0, 1) #rot
            self.rect = Rectangle(pos=self.pos, size=self.size)
    
    def update(self):
        #apply gravity
        self.velocity_y += self.gravity
        self.pos[1] += self.velocity_y

        jump_height = 0

        #check contact with ground
        if self.pos[1] <= 100: #ground hight
            self.pos[1] = 100
            jump_height = self.is_jumping
            self.velocity_y = 0
            self.is_jumping = 0

        #update position
        self.rect.pos = self.pos
        return jump_height

    def jump(self):
        if self.is_jumping < self.max_jumps:
            self.velocity_y = self.jump_strength
            self.is_jumping += 1