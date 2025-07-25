from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import logging

"""set up logging"""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Game")

class Start_screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Welcome to Jumpi!\nPress start to begin", font_size=20)
        start_button = Button(text="Start", size_hint=(0.5, 0.2), pos_hint={'center_x':0.5})
        start_button.bind(on_press=self.start_game)
        layout.add_widget(label)
        layout.add_widget(start_button)
        self.add_widget(layout)

        
    def start_game(self, instance):
        #game_screen = self.manager.get_screen('game')
        #game_screen.clean_up()
        self.manager.current = 'game' #change to game screen