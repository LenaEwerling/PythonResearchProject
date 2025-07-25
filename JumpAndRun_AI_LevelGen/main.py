from kivy.app import App
from jump_and_run import Game as Game
from Menu.start_screen import Start_screen as Menu
from Menu.GameScreenManager import  GameScreenManager

class GameApp(App):
    def build(self):
        sm = GameScreenManager()
        sm.add_widget(Menu(name='start'))
        sm.add_widget(Game(name='game'))
        sm.current = 'start'
        return sm

# start game
if __name__ == "__main__":
    # Game.JumpAndRunApp().run()
    GameApp().run()
