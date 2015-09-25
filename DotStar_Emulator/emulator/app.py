import sys
import logging
import logging.config
import os

import pygame
import pygame.font
from pygame import constants
import blinker
from six import reraise

from .vector2 import Vector2
from . import config
from .utils import vector2_to_int
from .scenes.running import RunningScene
from .scenes.about import AboutScene
from . import globals
from .data import StripData, MappingData, TCPReader
from .rate_counter import RateCounter
from .utils import MEDIA_PATH


pygame.init()

log = logging.getLogger("app")


def configure_logging():
    logging.config.dictConfig(config.get("LOGGING"))


class EmulatorApp(object):

    def __init__(self):
        """
        Main Emulator Application Class, runs the pygame Loop.

        :return:
        """

        # Set reference to self as current_app
        globals.current_app = self

        # Configure
        found_user_config = config.read_configuration()

        # Setup any logging configurations
        configure_logging()

        if found_user_config:
            log.info("Found user config file")

        # Create pygame window
        self.window_size = Vector2(config.get("WINDOW_SIZE"))
        self.window_caption = config.get("WINDOW_CAPTION")
        log.info("Creating window at %s resolution", self.window_size)
        full_screen = pygame.FULLSCREEN if config.get("FULL_SCREEN") else 0
        self.screen = pygame.display.set_mode(vector2_to_int(self.window_size),
                                              pygame.DOUBLEBUF | pygame.HWSURFACE | full_screen)
        pygame.display.set_caption(self.window_caption)

        # Setup pygame clock
        self.clock = pygame.time.Clock()
        self.fps_limit = 60  # easily set/change the fps limit with this variable

        # current scene to display
        self.scene = None

        # main loop truth
        self.running = True

        # Keep track if data has been read so we can trigger update
        self._data_read = False

        # subscribe to signals
        blinker.signal("event.keydown").connect(self.on_F4, sender=pygame.K_F4)
        blinker.signal("app.exit").connect(self.on_exit)
        blinker.signal("app.fps").connect(self.on_fps)
        blinker.signal("app.setscene").connect(self.on_setscene)

        # set references to data models
        # Mapping needs to be first, so strip_data can determine number of pixels needed
        globals.mapping_data = MappingData()
        globals.strip_data = StripData()

        # Stored fonts
        self.fonts = {}

        # Create running scene
        self.build_initial_scene()

        # Create Data Reader
        self.data_reader = TCPReader()

        # Create Rate Counter
        self.rate_counter = RateCounter()

    def on_fps(self, sender, fps):
        """
        Callback for setting the given frame per second rate limit.

        :param sender: blinker sender
        :param fps: `int`
        :return: None
        """

        self.fps_limit = fps
        log.info("FPS limit set to %s", fps)

    def on_exit(self, sender):
        """
        Callback for app.exit blinker event.  Stop the main loop from running.

        :param sender: blinker sender
        :return: None
        """
        self.running = False

    @staticmethod
    def on_F4(sender, event):
        """
        callback for keypress event.  Shutdown the app.

        :param sender: blinker sender
        :param event: pygame.event object
        :return: None
        """

        # Only trigger on Alt Keypress
        if event.mod in [pygame.KMOD_LALT, pygame.KMOD_RALT]:
            blinker.signal("app.exit").send(None)

    def get_font(self, size):
        """
        Get a and cache a pygame.freetype font in the given size.  Because they are cached if one font size
        has already been loaded just return it.  Else create it, store it then return it.
        :param size:
        :return:
        """

        name = os.path.join(MEDIA_PATH, 'inconsolata-lgc', 'Inconsolata-LGC.otf')

        key = "{}".format(size)

        if key not in self.fonts:
            font = pygame.font.Font(name, size)
            # font = pygame.freetype.Font(name, size)
            self.fonts[key] = font
        else:
            font = self.fonts[key]
        return font

    def build_initial_scene(self):
        """
        Setup the default scene on loading of the application.

        :return: None
        """

        self.scene = RunningScene()

    def on_setscene(self, sender, scene_name):
        """
        blinker signal callback to create and set a new scene.

        :param sender: blinker sender
        :param scene_name: `str` name of the scene to load
        :return: None
        """
        if scene_name == "about":
            self.scene = AboutScene()
        if scene_name == "running":
            self.scene = RunningScene()

    def run(self):

        # Start Threads
        self.data_reader.start()
        self.data_reader.startup.wait()
        if not self.data_reader.startup_success:
            return

        self.rate_counter.start()

        # store signals
        event_keydown = blinker.signal("event.keydown")
        event_mousedown = blinker.signal("event.mousebuttondown")
        event_mousemotion = blinker.signal("event.mousemotion")

        try:

            while self.running:

                if self._data_read:
                    blinker.signal("stripdata.updated").send(None)
                    self._data_read = False

                elapsed = self.clock.tick(self.fps_limit)

                # Process Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    # Turn keydown events into blinker signals
                    if event.type == pygame.KEYDOWN:

                        # Find pygame.constants.K_? reference. This is needed because blinker uses id(sender) in order
                        # to hash the sender.  This doesn't work with integers -5 through 256 because python will create
                        # a new object every time for other numbers.
                        for d in dir(constants):
                            if constants.__dict__[d] == event.key:
                                event_keydown.send(constants.__dict__[d], event=event)

                    # Turn mousebuttondown events into blinker signals
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        event_mousedown.send(event.button, event=event)

                    if event.type == pygame.MOUSEMOTION:
                        event_mousemotion.send(None, event=event)

                # Update things that care
                if self.scene:
                    self.scene.update(elapsed)
                globals.strip_data.update(elapsed)

                # Time to Render the Screen!
                self.screen.fill((0, 0, 0))

                if self.scene:
                    self.scene.on_draw(self.screen)

                pygame.display.flip()

        except KeyboardInterrupt:
            pass
        except:
            # Stop threads
            self.data_reader.stop()
            self.rate_counter.stop()
            # re-raise
            exc_info = sys.exc_info()
            reraise(exc_info[0], exc_info[1], exc_info[2])

        # Stop and Join threads
        self.data_reader.stop()
        self.rate_counter.stop()
        self.rate_counter.join()
        self.data_reader.join()

        # Not really needed, but its in most pygame examples.. hmmm.
        sys.exit()
