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
from environment import Player
from environment import Platform
from environment import Obstacle
from environment import Timer
from analysis import data_logger
from analysis import Analyzer

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
        self.timer = Timer.Timer(Window.height)
        self.analyzer = Analyzer.Analyzer()
        self.game_over = False
        self.load_parameters()
        self.logger = data_logger.DataLogger()
        self.call_adjust = False

        self.add_widget(self.platform)
        self.add_widget(self.player)
        self.add_widget(self.timer)

        """binding to Window size change"""
        Window.bind(on_resize=self.resize)

        """binding to key"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        """call update function regularely"""
        self.clock_event = Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        self.speed_event = Clock.schedule_interval(self.speed_up, self.change_interval)
        self.spawn_obstacle()

    def resize(self, window, width, height):
        self.timer.updateTimerPos(window.height)

    def load_parameters(self):
        with open('analysis/parameter.json', 'r') as f:
            params = json.load(f)
            self.speed = params['speed']
            self.change_interval = params['change_interval']
            self.speed_factor = params['speed_factor']
            self.spawn_interval = params['spawn_interval']
            self.spawn_factor = params['spawn_factor']
            self.obstacle_factor = params['obstacle_factor']


    def speed_up(self, dt):
        self.call_adjust = True

    def adjust_interval(self):
        self.speed *= self.speed_factor
        for obstacle in self.obstacles:
            obstacle.speed = self.speed
        self.spawn_interval *= self.spawn_factor
        if self.spawn_event:
            self.spawn_event.cancel()
        #self.spawn_obstacle()
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        logger.debug(f"Speed increased to {self.speed} and spawntime decreased to {self.spawn_interval}")

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self_keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar': #space for jumping
            self.player.jump()

    def spawn_obstacle(self, dt = 0):
        if not self.game_over:
            # weights = [
            #     (1 - self.obstacle_factor) ** i for i in range(Obstacle.Obstacle.obstacle_kind_count) #calculate weights based on difficulty factor
            # ][::1] #Umkehren so that 0 is weighted higher with lower factor
            # total = sum(weights)
            # weights = [w / total for w in weights] #normalize
            # obstacle_type = random.choices(range(Obstacle.Obstacle.obstacle_kind_count), weights=weights, k=1)[0]
            new_obstacle = Obstacle.Obstacle(self.obstacle_factor, self.speed)
            self.add_widget(new_obstacle)
            self.obstacles.append(new_obstacle)
            if (self.call_adjust):
                self.adjust_interval()
                self.call_adjust = False

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
            # self.time_elapsed += dt
            # self.timer_label.text = f"Time: {int(self.time_elapsed)}"
            self.timer.updateTimer(dt)

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
                    self.timer.gameOver()
                    logger.debug(f"Game over- Time survived: {self.timer.getTime()}")
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
        self.logger.time_survived = self.timer.getTime()
        self.logger.save_game_data()
        
class JumpAndRunApp(App):
    def build(self):
        return Game()