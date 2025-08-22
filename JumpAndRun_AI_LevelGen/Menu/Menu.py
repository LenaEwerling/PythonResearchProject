from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
import logging
import csv
import json
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.graphics import Color, Rectangle
import matplotlib.pyplot as plt
from kivy.lang import Builder

"""Load the .kv file for UI layout."""
Builder.load_file('Menu/Menu.kv')

"""Set up logging."""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.WARNING)

"""Set standard font for Matplotlib."""
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['font.size'] = 14

class Menu(Screen):
    """Menu screen class for displaying game stats and starting the game."""
    def __init__(self, **kwargs):
        """Initialize the menu screen with chart types."""
        super().__init__(**kwargs)
        self.chart_types = [
            {'name': 'Time Survived', 'data_key': 1, 'ylabel': 'Time (seconds)', 'chart_type': 'bar'},
            {'name': 'Obstacles Mastered', 'data_key': 7, 'ylabel': 'Count', 'chart_type': 'bar'},
            {'name': 'Death Causes', 'data_key': 10, 'ylabel': 'Frequency', 'chart_type': 'hist'},
            {'name': 'Movements vs Obstacles', 'data_keys': [8, 9], 'ylabel': 'Count', 'chart_type': 'grouped_overlapping'},
        ]
        self.current_chart_index = 0
        self.current_canvas = None  # Stores the current canvas widget

    def on_enter(self):
        """Called when the menu screen is displayed."""
        self.load_stats()
        
    def start_game(self):
        """Switch to the game screen."""
        self.manager.current = 'game'

    def switch_chart(self, direction):
        """Switch to the next or previous chart type."""
        self.current_chart_index = (self.current_chart_index + direction) % len(self.chart_types)
        logger.debug(f"Switched to chart index: {self.current_chart_index}")
        self.load_stats()

    def load_stats(self):
        """Load and display game statistics from CSV."""
        logger.debug("load_stats")
        try:
            with open("data/game_data.csv", "r", newline="") as file:
                reader = csv.reader(file)
                stats = list(reader)
                if stats:
                    # Get the last entry for stats
                    last_entry = stats[-1]
                    try:
                        time_survived = float(last_entry[1].strip()) if last_entry[1] and last_entry[1].strip() else 0.0
                    except ValueError:
                        time_survived = 0.0
                        logger.error(f"invalid entry in csv for time_survived: {last_entry[1]}")
                    try:
                        obstacles_count = int(last_entry[7].strip()) if last_entry[7] and last_entry[7].strip() else 0
                    except ValueError:
                        obstacles_count = 0
                        logger.error(f"invalid entry in csv for obstacles_count: {last_entry[7]}")
                    death_cause = last_entry[10]
                    classification = last_entry[11]
                    difficulty = float(last_entry[12].strip()) if last_entry[12] and last_entry[12].strip() else 0.0
                    difficulty = round(difficulty*10, 2)
                    stats_text = f"Last round: \nTime: {time_survived:.1f} seconds\nObstacles mastered: {obstacles_count}\nDeath cause: {death_cause}\nDifficulty: {classification} ({difficulty})"
                    self.ids.stats_label.text = stats_text
                    logger.debug(f"loaded stats: {stats_text}")

                    # Prepare data for the current chart type
                    current_chart = self.chart_types[self.current_chart_index]
                    if current_chart['chart_type'] == 'grouped_overlapping':
                        data_keys = current_chart['data_keys']  # [8, 9] for obstacles and movements
                        data = {}
                        matching_entries = [last_entry]  # Only current round
                        for entry in matching_entries:
                            obstacles = json.loads(entry[data_keys[0]].replace("'", '"'))  # Parse obstacles
                            movements = json.loads(entry[data_keys[1]].replace("'", '"'))  # Parse movements
                            data['obstacles'] = {item['name']: item['count'] for item in obstacles}
                            data['movements'] = {item['name']: item['count'] for item in movements}
                    else:    
                        data_key = current_chart['data_key']
                        data = []
                        matching_entries = [entry for entry in reversed(stats) if entry[11] == classification]
                        if current_chart['chart_type'] == 'bar':
                            matching_entries = matching_entries[:5]
                        for entry in reversed(matching_entries):
                            try:
                                value = entry[data_key].strip() if entry[data_key] and entry[data_key].strip() else ""
                                if current_chart['chart_type'] == 'bar':
                                    value = float(value) if value else 0.0
                                data.append(value)
                            except ValueError:
                                data.append(0.0 if current_chart['chart_type'] == 'bar' else "")
                                logger.error(f"invalid entry in csv for data_key {data_key}: {entry[data_key]}")

                    self.create_chart(data, current_chart['name'], current_chart['ylabel'], classification, current_chart['chart_type'])
                else:
                    logger.debug("No statistics available")

        except FileNotFoundError:
            logger.error("game_data.csv not found")
        except Exception as e:
            logger.error(f"Error while loading statistics: {str(e)}")

    def create_chart(self, data, title, ylabel, difficulty_classification, chart_type):
        """Create and display a Matplotlib chart for game statistics."""
        logger.debug(f"Data for chart: {data}")

        # Close the old figure if it exists
        if plt.fignum_exists(plt.gcf().number):
            plt.close()

        # Create a new figure and axis for the chart
        fig = plt.figure(figsize=(6, 3))
        ax = fig.add_subplot(1, 1, 1)

        if chart_type == 'bar':
            length = len(data)
            labels = [str(-(length) + i) for i in range(1, length + 1)]
            if length > 0:
                labels[-1] = "current"
            ax.bar(labels, data, width=0.6, color='blue')
            ax.set_xlabel(f'Rounds on difficulty: {difficulty_classification}')

        elif chart_type == 'hist':
            unique_causes = list(set(data))
            counts = [data.count(cause) for cause in unique_causes]
            logger.warning(f"Unique causes: {unique_causes}, Counts: {counts}")
            ax.bar(unique_causes, counts, color=['red', 'green', 'blue', 'orange', 'purple'][:len(unique_causes)])
            ax.set_xlabel('Death Causes')

        elif chart_type == 'grouped_overlapping':
               x = [0, 0.2, 1, 1.2]  # Positions: Single Jump, low blocks, Double Jumps, high blocks
               width = 0.15  # Reduced width for overlapping
               single_jumps = data['movements'].get('single_jump', 0)
               low_blocks = data['obstacles'].get('low_block', 0)
               double_jumps = data['movements'].get('double_jump', 0)
               high_blocks = data['obstacles'].get('high_block', 0)
               ax.bar(x[0], single_jumps, width, color='blue', label='Single Jumps')
               ax.bar(x[1], low_blocks, width, color='red', label='Low Blocks')
               ax.bar(x[2], double_jumps, width, color='green', label='Double Jumps')
               ax.bar(x[3], high_blocks, width, color='orange', label='High Blocks')
               ax.set_xticks([0.1, 1.1])  # Center positions of groups
               ax.set_xticklabels(['Single Jump', 'Double Jumps'])
               ax.legend()

        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.margins(x=0.2)
        fig.tight_layout()

        def add_canvas(dt):
            """Add the Matplotlib canvas to the Kivy layout."""
            try:
                if self.current_canvas:
                    self.ids.chart_placeholder.remove_widget(self.current_canvas)
                canvas = FigureCanvasKivyAgg(fig)
                self.current_canvas = canvas
                canvas.size_hint = (None, None)
                canvas.size = self.ids.chart_placeholder.size
                canvas.pos = self.ids.chart_placeholder.pos
                self.ids.chart_placeholder.clear_widgets()
                self.ids.chart_placeholder.add_widget(canvas)
                canvas.draw()
                self.ids.chart_placeholder.canvas.ask_update()
                self.ids.chart_placeholder.bind(
                    size=lambda instance, value: setattr(canvas, 'size', value),
                    pos=lambda instance, value: setattr(canvas, 'pos', value)
                )
            except AttributeError as e:
                logger.error(f"Error while creating Canvas: {str(e)}")
                self.ids.stats_label.text += "\nError while creating Diagram"

        Clock.schedule_once(add_canvas, 0.5)
