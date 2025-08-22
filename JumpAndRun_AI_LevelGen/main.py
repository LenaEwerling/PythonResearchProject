from kivy.app import App
# Import the Game class from jump_and_run module
from jump_and_run import Game as Game
# Import the Menu class from Menu module
from Menu.Menu import Menu as Menu
# Import the GameScreenManager class from Menu module
from Menu.GameScreenManager import  GameScreenManager

class GameApp(App):
    """Main application class for the Jump & Run game."""
    def build(self):
        """Build the screen manager for the game."""
        # Create a screen manager to handle different screens
        sm = GameScreenManager()
        # Add the menu screen
        sm.add_widget(Menu(name='start'))
        # Add the game screen
        sm.add_widget(Game(name='game'))
        # Set the initial screen to the menu
        sm.current = 'start'
        return sm

# Start the game if this script is run directly
if __name__ == "__main__":
    GameApp().run()