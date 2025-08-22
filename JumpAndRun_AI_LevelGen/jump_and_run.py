from os import write
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import logging
import json
from environment import Player
from environment import Platform
from environment import Obstacle
from environment import Timer
from analysis import data_logger
from analysis import Analyzer

"""Set up logging."""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Game")

class Game(Screen):
    """Main game screen class that handles gameplay logic."""
    def __init__(self, **kwargs):
        """Initialize the game screen with necessary components."""
        super().__init__(**kwargs)
        # Create a vertical layout for the game elements
        self.layout = BoxLayout(orientation='vertical')
        # Initialize the player object
        self.player = Player.Player()
        # Initialize the platform object
        self.platform = Platform.Platform()
        # List to hold obstacle objects
        self.obstacles = []
        # Initialize the timer at the top of the window
        self.timer = Timer.Timer(Window.height)
        # Initialize the analyzer for game data
        self.analyzer = Analyzer.Analyzer()
        # Flag to check if the game is running
        self.game_running = False
        # Load game parameters from JSON
        self.load_parameters()
        # Initialize the data logger
        self.data_logger = data_logger.DataLogger()
        # Flag to adjust game difficulty
        self.call_adjust = False

        # Add platform to the screen
        self.add_widget(self.platform)
        # Add player to the screen
        self.add_widget(self.player)
        # Add timer to the screen
        self.add_widget(self.timer)

        """Binding to window size change event."""
        Window.bind(on_resize=self.resize)

        """Binding to keyboard input."""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    def initiate_schedulers(self):
        """Schedule game update functions."""
        # Schedule the main update loop at 60 FPS
        self.clock_event = Clock.schedule_interval(self.update, 1.0 / 60.0)
        # Schedule obstacle spawning
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        # Schedule speed increase
        self.speed_event = Clock.schedule_interval(self.speed_up, self.change_interval)
        # Spawn the first obstacle
        self.spawn_obstacle()

    def quit_schedulers(self):
        """Cancel all scheduled game update functions."""
        if hasattr(self, 'clock_event'):
            self.clock_event.cancel()
        if hasattr(self, 'spawn_event'):
            self.spawn_event.cancel()
        if hasattr(self, 'speed_event'):
            self.speed_event.cancel()

    def on_enter(self):
        """Called when the screen is displayed."""
        # Load parameters when entering the game screen
        self.load_parameters()
        # Reset obstacles cleared count
        self.data_logger.obstacles_cleared = 0
        # Start the game
        self.game_running = True
        # Initiate update schedulers
        self.initiate_schedulers()

    def clean_up(self):
        """Clean up game elements when game ends."""
        # Remove all obstacles from the screen
        for obstacle in self.obstacles[:]:
            self.remove_widget(obstacle)
        self.obstacles = []
        # Reset timer
        self.timer.setTime(0)
        # Reset player
        self.player.reset()
        # Cancel schedulers
        self.quit_schedulers()

    def resize(self, window, width, height):
        """Update timer position on window resize."""
        self.timer.updateTimerPos(window.height)

    def load_parameters(self):
        """Load game parameters from JSON file."""
        with open('analysis/parameter.json', 'r') as f:
            params = json.load(f)
            self.speed = params['speed']
            self.change_interval = params['change_interval']
            self.speed_factor = params['speed_factor']
            self.spawn_interval = params['spawn_interval']
            self.spawn_factor = params['spawn_factor']
            self.obstacle_factor = params['obstacle_factor']

    def speed_up(self, dt):
        """Flag to adjust game speed."""
        self.call_adjust = True

    def adjust_interval(self):
        """Adjust game speed and spawn interval."""
        self.speed *= self.speed_factor
        for obstacle in self.obstacles:
            obstacle.speed = self.speed
        self.spawn_interval *= self.spawn_factor
        if self.spawn_event:
            self.spawn_event.cancel()
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, self.spawn_interval)
        logger.debug(f"Speed increased to {self.speed} and spawntime decreased to {self.spawn_interval}")

    def _keyboard_closed(self):
        """Unbind keyboard when closed."""
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self_keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle key press events."""
        if keycode[1] == 'spacebar': #space for jumping
            self.player.jump()

    def spawn_obstacle(self, dt = 0):
        """Spawn a new obstacle if the game is running."""
        if self.game_running:
            new_obstacle = Obstacle.Obstacle(self.obstacle_factor, self.speed)
            self.add_widget(new_obstacle)
            self.obstacles.append(new_obstacle)
            if (self.call_adjust):
                self.adjust_interval()
                self.call_adjust = False

    def check_collision(self, player, obstacle):
        """Simple rectangle collision check between player and obstacle."""
        if not player or not obstacle:
            return False

        player = (player.pos[0], player.pos[1], player.size[0], player.size[1])
        obstacle = (obstacle.pos[0], obstacle.pos[1], obstacle.size[0], obstacle.size[1])

        return (player[0] < obstacle[0] + obstacle[2] and 
                player[0] + player[2] > obstacle[0] and
                player[1] < obstacle[1] + obstacle[3] and
                player[1] + player[3] > obstacle[1])

    def update(self, dt):
        """Main game update loop."""
        if self.game_running:
            self.timer.updateTimer(dt)
            self.log_jump(self.player.update())

            """Update obstacles."""
            for obstacle in self.obstacles[:]:
                if obstacle in self.children:
                    obstacle.update()
                
                """Remove obstacles leaving the screen."""
                if obstacle.pos[0] < -obstacle.size[0]:
                    self.remove_widget(obstacle)
                    self.obstacles.remove(obstacle)
                elif self.check_collision(self.player, obstacle):
                    """Check for collision."""
                    self.game_running = False
                    self.timer.gameOver()
                    logger.debug(f"Game over- Time survived: {self.timer.getTime()}")
                    self.quit_schedulers()
                    self.player.reset()
                    self.log_end_of_game(obstacle)
                    self.analyzer.analyze()
                    self.clean_up()
                    self.manager.current = 'start' #back to start screen
                else:
                    self.check_passed_obstacle(obstacle)

    def check_passed_obstacle(self, obst):
        """Checks whether player has passed an obstacle."""
        if obst.x + obst.width < self.player.x and obst.counted == False:
            obst.counted = True
            self.data_logger.obstacles_cleared += 1
            for obstacle in self.data_logger.kinds_of_obstacles_cleared:
                if obstacle["name"] == obst.type:
                    obstacle["count"] += 1

    def log_jump(self, jump_height):
        """Logs jump movements."""
        if jump_height != 0:
            name = ""
            match jump_height:
                case 1:
                    name = "single_jump"
                case 2:
                    name = "double_jump"
            for movement in self.data_logger.kinds_of_movement:
                if movement["name"] == name:
                    movement["count"] += 1

    def log_end_of_game(self, death_causing_obstacle):
        """Logs end stats of game."""
        self.data_logger.speed_at_end = self.speed
        self.data_logger.change_interval = self.change_interval
        self.data_logger.speed_factor = self.speed_factor
        self.data_logger.spawn_interval = self.spawn_interval
        self.data_logger.spawn_factor = self.spawn_factor
        self.data_logger.death_cause = death_causing_obstacle.type
        self.data_logger.time_survived = self.timer.getTime()
        self.data_logger.save_game_data()