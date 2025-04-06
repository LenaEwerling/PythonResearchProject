from os import write
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
import random
import logging
import json

#import pygame
import time
#import config
import Player
import Platform
import Obstacle
import data_logger
import Analyzer

"""set up logging"""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Game")

class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        Window.clearcolor = (0.2, 0.2, 0.2, 1)

        self.player = Player.Player()
        self.platform = Platform.Platform()
        self.obstacles = [] #list of obstacles
        self.analyzer = Analyzer.Analyzer()
        self.game_over = False
        self.time_elapsed = 0 #Timer in seconds
        self.load_parameters()
        self.logger = data_logger.DataLogger()

        """Timer label top left"""
        self.timer_label = Label(
            text="Time: 0",
            size_hint=(None, None),
            size=(100,30),
            font_size=20,
            color=(0,1,0,1)
        )
        self.timer_label.pos = (10, Window.height - self.timer_label.height - 10)

        self.add_widget(self.platform)
        self.add_widget(self.player)
        self.add_widget(self.timer_label)

        """binding to Window size change"""
        Window.bind(on_resize=self.update_timer_pos)

        """binding to key"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        """call update function regularely"""
        self.clock_event = Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        self.speed_event = Clock.schedule_interval(self.speed_up, self.change_interval)

    def load_parameters(self):
        with open('parameter.json', 'r') as f:
            params = json.load(f)
            self.speed = params['speed']
            self.change_interval = params['change_interval']
            self.speed_factor = params['speed_factor']
            self.spawn_interval = params['spawn_interval']
            self.spawn_factor = params['spawn_factor']


    def speed_up(self, dt):
        self.speed *= self.speed_factor
        for obstacle in self.obstacles:
            obstacle.speed = self.speed
        self.spawn_interval *= self.spawn_factor
        if self.spawn_event:
            self.spawn_event.cancel()
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        logger.debug(f"Speed increased to {self.speed} and spawntime decreased to {self.spawn_interval}")

    def update_timer_pos(self, window, width, height):
        self.timer_label.pos = (10, height - self.timer_label.height - 10)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self_keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar': #space for jumping
            self.player.jump()

    def spawn_obstacle(self, dt):
        if not self.game_over:
            obstacle_type = random.randrange(0,2)
            new_obstacle = Obstacle.Obstacle(obstacle_type, self.speed)
            self.add_widget(new_obstacle)
            self.obstacles.append(new_obstacle)

    def check_collision(self, player, obstacle):
        """simple rectangle collision check"""
        px, py = player.pos
        pw, ph = player.size
        ox, oy = obstacle.pos
        ow, oh = obstacle.size

        return (px < ox + ow and 
                px + pw > ox and
                py < oy + oh and
                py + ph > oy)

    def update(self, dt):
        if not self.game_over:
            """update timer"""
            self.time_elapsed += dt
            self.timer_label.text = f"Time: {int(self.time_elapsed)}"
            #logger.debug(f"Timer label updated: text={self.timer_label.text}, pos={self.timer_label.pos}, exists={self.timer_label in self.children}")

            #self.player.update()
            self.log_jump(self.player.update())

            """update obstacles"""
            for obstacle in self.obstacles[:]:
                if obstacle in self.children:
                    obstacle.update()
                
                """remove obstacles leaving the screen"""
                if obstacle.pos[0] < -obstacle.size[0]:
                    self.remove_widget(obstacle)
                    self.obstacles.remove(obstacle)
                elif self.check_collision(self.player, obstacle):
                    """check for collision"""
                    self.game_over = True
                    self.timer_label.size = (200, 30)
                    self.timer_label.text = f"Game over! Time: {int(self.time_elapsed)}" 
                    logger.debug(f"Game over: {self.timer_label.text}")
                    self.clock_event.cancel()
                    self.spawn_event.cancel()
                    self.speed_event.cancel()
                    self.log_end_of_game(obstacle)
                    self.analyzer.analyze()
                else:
                    self.check_passed_obstacle(obstacle)

    def check_passed_obstacle(self, obst):
        """checks whether player has passed an obstacle"""
        if obst.x + obst.width < self.player.x and obst.counted == False:
            obst.counted = True
            self.logger.obstacles_cleared += 1
            for obstacle in self.logger.kinds_of_obstacles_cleared:
                if obstacle["name"] == obst.type:
                    obstacle["count"] += 1

    def log_jump(self, jump_height):
        if jump_height != 0:
            name = ""
            match jump_height:
                case 1:
                    name = "single_jump"
                case 2:
                    name = "double_jump"
            for movement in self.logger.kinds_of_movement:
                if movement["name"] == name:
                    movement["count"] += 1

    def log_end_of_game(self, death_causing_obstacle):
        """logs end stats of game"""
        self.logger.speed_at_end = self.speed
        self.logger.change_interval = self.change_interval
        self.logger.speed_factor = self.speed_factor
        self.logger.spawn_interval = self.spawn_interval
        self.logger.spawn_factor = self.spawn_factor
        self.logger.death_cause = death_causing_obstacle.type
        self.logger.time_survived = self.time_elapsed
        self.logger.save_game_data()
        
class JumpAndRunApp(App):
    def build(self):
        return Game()