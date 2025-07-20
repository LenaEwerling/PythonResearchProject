from kivy.uix.widget import Widget
from kivy.uix.label import Label

class Timer(Widget):
    def __init__(self, windowHeight, **kwargs):
        super().__init__(**kwargs)
        self.timeElapsed = 0
        self.windowHeight = windowHeight

        """Timer label top left"""
        self.timerLabel = Label(
            text="Time: 0",
            size_hint=(None, None),
            size=(100,30),
            font_size=20,
            color=(0,1,0,1) #green
        )
        self.add_widget(self.timerLabel)

    def draw(self):
        self.timerLabel.pos = (10, self.windowHeight - self.timerLabel.height - 10)

    def updateTimer(self, delta_time):
        self.timeElapsed += delta_time
        self.timerLabel.text = f"Time: {int(self.timeElapsed)}"

    def updateTimerPos(self, height):
        self.timerLabel.pos = (10, height - self.timerLabel.height - 10)

    def gameOver(self):
        self.timerLabel.size = (200, 30)
        self.timerLabel.text = f"Game over! Time: {int(self.timeElapsed)}" 

    def getTime(self):
        return self.timeElapsed
    