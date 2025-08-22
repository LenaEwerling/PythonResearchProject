from kivy.uix.widget import Widget
from kivy.uix.label import Label

class Timer(Widget):
    """Timer class for tracking game time."""
    def __init__(self, windowHeight, **kwargs):
        """Initialize the timer with position and label."""
        super().__init__(**kwargs)
        self.timeElapsed = 0
        self.windowHeight = windowHeight

        """Timer label top left."""
        self.timerLabel = Label(
            text="Time: 0",
            size_hint=(None, None),
            size=(100,30),
            font_size=20,
            color=(0,1,0,1) # green
        )
        self.add_widget(self.timerLabel)

    def draw(self):
        """Draw the timer label."""
        self.timerLabel.pos = (10, self.windowHeight - self.timerLabel.height - 10)

    def updateTimer(self, delta_time):
        """Update the elapsed time and label text."""
        self.timeElapsed += delta_time
        self.timerLabel.text = f"Time: {int(self.timeElapsed)}"

    def updateTimerPos(self, height):
        """Update timer label position on window resize."""
        self.timerLabel.pos = (10, height - self.timerLabel.height - 10)

    def gameOver(self):
        """Display game over message with final time."""
        self.timerLabel.size = (200, 30)
        self.timerLabel.text = f"Game over! Time: {int(self.timeElapsed)}" 

    def getTime(self):
        """Get the elapsed time."""
        return self.timeElapsed

    def setTime(self, time):
        """Set the elapsed time."""
        self.timeElapsed = time
    