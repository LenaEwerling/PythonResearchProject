from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
import logging
import csv
#from kivy_garden.graph import Graph, BarPlot
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.graphics import Color, Rectangle
# import matplotlib
import matplotlib.pyplot as plt
# from matplotlib import style
# from matplotlib.figure import Figure
from kivy.lang import Builder
from kivy.clock import Clock

"""load .kv-File"""
Builder.load_file('Menu/Menu.kv')

"""set up logging"""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.WARNING)


"""set standard font for matplotlib"""
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

class Menu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.load_stats()
        
    def start_game(self):
        self.manager.current = 'game' #change to game screen

    def load_stats(self):
        logger.debug("load_stats")
        try:
            with open("data/game_data.csv", "r", newline="") as file:
                reader = csv.reader(file)
                stats = list(reader)
                if stats:
                    # last round
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
                        logger.error(f"invalid entry in csv for obstcles_count: {last_entry[7]}")
                    death_cause = last_entry[10]
                    stats_text = f"Last round: \nTime: {time_survived:.1f} seconds\nObstacles mastered: {obstacles_count}\nDeath cause: {death_cause}"
                    self.ids.stats_label.text = stats_text
                    logger.debug(f"loaded stats: {stats_text}")

                    # last 5 times - barchart
                    last_5_times = []
                    for entry in stats[-5:]:
                        try:
                            time = float(entry[1].strip()) if entry[1] and entry[1].strip() else 0.0
                            last_5_times.append(time)
                        except ValueError:
                            last_5_times.append(0.0)
                            logger.error(f"invalid entry in csv for time: {entry[1]}")

                    self.create_bar_chart(last_5_times)
                else:
                    logger.debug("No statistics available")

        except FileNotFoundError:
            logger.error("game_data.csv not found")
        except Exception as e:
            logger.error(f"Error while loading statistics: {str(e)}")

    def create_bar_chart(self, times):
        logger.debug(f"Times for bar chart: {times}")
        logger.debug(f"chart_placeholder size: {self.ids.chart_placeholder.size}")
        logger.debug(f"chart_placeholder pos: {self.ids.chart_placeholder.pos}")

        # Erstelle das Diagramm
        fig = plt.figure(figsize=(6, 3))
        logger.debug("Figure created")
        ax = fig.add_subplot(1, 1, 1)
        labels = [f"{i+1}" for i in range(len(times))]
        logger.warning(labels)
        ax.bar(labels, times, width=0.6, color='blue')
        ax.set_xlabel('Rounds')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Time survived')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.margins(x=0.2)
        fig.tight_layout()

        def add_canvas(dt):
            try:
                canvas = FigureCanvasKivyAgg(fig)
                logger.debug(f"canvas created: {canvas.size}")
                canvas.size_hint = (None, None)  # Deaktiviere size_hint
                canvas.size = self.ids.chart_placeholder.size
                canvas.pos = self.ids.chart_placeholder.pos
                logger.debug(f"canvas set: size={canvas.size}, pos={canvas.pos}")
                self.ids.chart_placeholder.clear_widgets()
                logger.debug("cleared widget")
                self.ids.chart_placeholder.add_widget(canvas)
                logger.debug("add widget")
                self.ids.chart_placeholder.canvas.ask_update()
                logger.debug("add widget and update canvas")
                # Binde Größe und Position dynamisch
                self.ids.chart_placeholder.bind(
                    size=lambda instance, value: setattr(canvas, 'size', value),
                    pos=lambda instance, value: setattr(canvas, 'pos', value)
                )
                logger.debug("bound size and pos")
                logger.warning(f"Canvas size after add: {canvas.size}")
                logger.warning(f"Canvas position after add: {canvas.pos}")
            except AttributeError as e:
                logger.error(f"Error while creating Canvas: {str(e)}")
                self.ids.stats_label.text += "\nError while creating Diagram"

        # Verzögere die Ausführung weiter, um Layout-Initialisierung sicherzustellen
        Clock.schedule_once(add_canvas, 0.5)

