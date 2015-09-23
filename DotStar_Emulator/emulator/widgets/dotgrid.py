import logging

import pygame
from pygame import Rect
from pygame.math import Vector2
import blinker

from DotStar_Emulator.emulator import config, globals
from DotStar_Emulator.emulator.gui.widget import Widget
from DotStar_Emulator.emulator.utils import vector2_to_floor, vector2_to_int

log = logging.getLogger("app")


class DotGridWidget(Widget):
    def __init__(self, use_surface=True):
        """
        Main display of DotStar Grid.

        Renders each LED in a x, y grid fashion.  Each grid cell is a LED.  Each grid cell can have its own borders.
        The main grid can also have a grid.

        Configuration [
            'GRID_SIZE': (x, y),  # Grid size
            'BORDER_SIZE': (x, y),  # Pixel size of the border drawn around each LED
            'PERIMETER_BORDER_SIZE': (x, y)  # Pixel size of the border drawn around the whole grid
            'GRID_BACKGROUND_COLOR': (r, g, b) or pygame.Color  # Color of the border/background of the grid
            'SQUARE_LED': True or False  # if True the LED's will be square, else fit to screen.
        ]

        :param use_surface: `bool`, default=True, use a surface to render the widget
        :return:
        """

        super(DotGridWidget, self).__init__(use_surface=use_surface)

        # Add a margin around the grid
        self.layout.margin.set(*[5 for i in range(4)])

        self.grid_size = None  # Number Columns, Rows of the grid
        self.cell_size = None  # Pixel size of each grid cell

        self.led_surface = None  # Reusable surface to render LEDs
        self.led_size = None  # Pixel size of the colored led inside the grid cell
        self.border_size = None  # Pixel size of the border to draw around the LED inside the grid cell
        self.grid_background_position = None  # pixel offset of background surface
        self.grid_background_surface = None  # background surface
        self.perimeter_border_size = None  # pixel size of perimeter border
        self.led_rects = None  # Cache the Rects of the LEDs, positioned to this widget
        self.grid_rects = None  # Cache the Rects of the grid Rects, position to this widget

        self.draw_borders = config.get("DRAW_BORDERS")  # Borders around each LED can be toggled on and off
        self.draw_indexes = config.get("DRAW_INDEXES")  # Borders around each LED can be toggled on and off
        self.draw_indexes_colors = config.get("DRAW_INDEXES_COLORS")

        # connect to signal used to toggle the borders.
        blinker.signal("dotgrid.drawborders").connect(self.on_drawborders)
        blinker.signal("dotgrid.drawindexes").connect(self.on_drawindexs)
        blinker.signal("stripdata.updated").connect(self.on_data_updated)

    def on_data_updated(self, sender):
        """
        Event callback when the strip_data has received updated data

        :param sender: blinker sender
        :return: None
        """

        self.redraw()

    def on_drawborders(self, sender, draw_borders):
        """
        Event callback to toggle the draw borders

        :param sender: blinker signal sender
        :param draw_borders: boolean
        :return: None
        """

        self.draw_borders = draw_borders
        self.initialize_grid()
        self.redraw()

    def on_drawindexs(self, sender, draw_indexes):
        """
        Event callback to toggle the draw indexs

        :param sender: blinker signal sender
        :param draw_indexes: boolean
        :return: None
        """

        self.draw_indexes = draw_indexes
        self.initialize_grid()
        self.redraw()

    def on_fit(self):
        """
        The grid is dependent of the size of the Widget, so after it has been fit, initialize the grid.

        :return: None
        """

        self.initialize_grid()

    def max_grid_pixel_size(self):
        """
        Calculate the max grid size in pixels.  Takes into account the layout of the right panel.
        :return: Vector2, max grid size in pixels
        """

        max_width = self.layout.rect.width - (self.perimeter_border_size.x * 2)
        max_height = self.layout.rect.height - (self.perimeter_border_size.y * 2)

        return Vector2(max_width, max_height)

    def create_background(self):
        """
        Calculates the background size and position, and creates the surface.

        :return: None
        """

        # Initial background Size
        background_size_px = Vector2(self.grid_size.x * self.cell_size.x,
                                     self.grid_size.y * self.cell_size.y)
        # add in perimeter border size

        background_size_px.x += (self.perimeter_border_size.x * 2)
        background_size_px.y += (self.perimeter_border_size.y * 2)

        self.grid_background_surface = pygame.Surface(vector2_to_int(background_size_px))

        if self.draw_borders > 0:
            color = config.get("DRAW_BORDERS_COLORS")[self.draw_borders - 1]
            self.grid_background_surface.fill(color)

        grid_background_position_rect = self.grid_background_surface.get_rect()
        grid_background_position_rect.centerx = self.layout.size.x / 2
        grid_background_position_rect.centery = self.layout.size.y / 2

        # Center the grid background in its space
        self.grid_background_position = Vector2(grid_background_position_rect.topleft)

    def calculate_cell_size(self, max_grid_pixel_size):
        """
        Given the max grid pixel size, determine the size of the individual grid cells.

        :param max_grid_pixel_size: pygame.math.Vector2 of the max size of the whole grid.
        :return: None
        """

        width = max_grid_pixel_size.x / float(self.grid_size.x)
        height = max_grid_pixel_size.y / float(self.grid_size.y)

        # Check that the LED size is at least 1px
        if width <= 1.0 or height <= 1.0:
            log.error("Calculated LED cell size less than 1 pixel.  The WINDOW_SIZE is to small to fit "
                      "the configured GRID_SIZE")
            raise Exception("LED size less than 1 pixel")

        # Sqaure up the LED
        if config.get("SQUARE_LED"):
            if width < height:
                height = width
            else:
                width = height

        self.cell_size = vector2_to_floor(Vector2(width, height))

    def calculate_led_size(self):
        """
        Calculate the led size for each cell.

        :return: None
        """

        if self.draw_borders:
            self.border_size = Vector2(config.get("BORDER_SIZE"))
        else:
            self.border_size = Vector2(0, 0)

        width = self.cell_size.x - (self.border_size.x * 2)
        height = self.cell_size.y - (self.border_size.y * 2)

        self.led_size = vector2_to_floor(Vector2(width, height))

        self.led_surface = pygame.Surface(self.led_size)

        # Check that the LED size is at least 1px
        if self.led_size.x <= 1.0 or self.led_size.y <= 1.0:
            log.error("LED border size is to large for calculated LED size '(%s, %s) pixels'",
                      self.cell_size.x, self.cell_size.y)
            raise Exception("LED border size is to large.")

    def initialize_grid(self):
        """
        Step through all of the calculations to determine the grid size and led size.

        :return: None
        """

        # Store Grid Size
        self.grid_size = Vector2(config.get("GRID_SIZE"))
        if self.draw_borders:
            self.perimeter_border_size = Vector2(config.get("PERIMETER_BORDER_SIZE"))
        else:
            self.perimeter_border_size = Vector2(0, 0)

        # Calculate cell_size
        self.calculate_cell_size(self.max_grid_pixel_size())

        # Create Background
        self.create_background()

        # Calculate LED Size
        self.calculate_led_size()

        log.info("LED size calculated %s, with borders %s", self.led_size, self.cell_size)

        # store led rects, of just the LED rect
        self.led_rects = [[None for x in range(int(self.grid_size.y))] for y in range(int(self.grid_size.x))]
        # each grid cells rect, includes led borders
        self.grid_rects = [[None for x in range(int(self.grid_size.y))] for y in range(int(self.grid_size.x))]

        for x in range(int(self.grid_size.x)):
            for y in range(int(self.grid_size.y)):

                top = self.grid_background_position.y + (self.cell_size.y * y)
                left = self.grid_background_position.x + (self.cell_size.x * x)
                top += self.border_size.y
                left += self.border_size.x
                top += self.perimeter_border_size.y
                left += self.perimeter_border_size.x

                width = self.cell_size.x - (self.border_size.x * 2)
                height = self.cell_size.y - (self.border_size.y * 2)

                rect = pygame.Rect(left, top, width, height)
                self.led_rects[x][y] = rect

                top = self.grid_background_position.y + (self.cell_size.y * y) + self.perimeter_border_size.y
                left = self.grid_background_position.x + (self.cell_size.x * x) + self.perimeter_border_size.x

                width = self.cell_size.x
                height = self.cell_size.y

                rect = Rect(left, top, width, height)
                self.grid_rects[x][y] = rect

    def on_render(self):

        self.surface.fill((0, 0, 0, 0))

        # if self.draw_borders > 0:
        self.surface.blit(self.grid_background_surface, self.grid_background_position)

        bg_color = config.get("DRAW_BORDERS_COLORS")[self.draw_borders - 1]

        # adjust font size for pixel index rendering based on size of the pixel
        if self.led_size.x >= 30 and self.led_size.y >= 30:
            font = globals.current_app.get_font(18)
        else:
            font = globals.current_app.get_font(8)

        for y in range(int(self.grid_size.y)):
            for x in range(int(self.grid_size.x)):
                index = globals.mapping_data.get(x, y)
                if index is not None:
                    c, b, g, r = globals.strip_data.get(index)
                    color = (r, g, b)
                else:
                    color = bg_color
                self.led_surface.fill(color)
                if index is not None and self.draw_indexes > 0:
                    text, text_pos = font.render(str(index), self.draw_indexes_colors[self.draw_indexes - 1])
                    text_pos.center = self.led_surface.get_rect().center
                    self.led_surface.blit(text, text_pos)
                self.surface.blit(self.led_surface, self.led_rects[x][y])


