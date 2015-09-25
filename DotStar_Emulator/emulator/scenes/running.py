import blinker
import pygame

from DotStar_Emulator.emulator import globals, config
from DotStar_Emulator.emulator.scene import Scene
from DotStar_Emulator.emulator.gui import panels
from DotStar_Emulator.emulator.gui import TextLabelWidget, ButtonWidget
from DotStar_Emulator.emulator.widgets.logo import LogoWidget
from DotStar_Emulator.emulator.widgets.dotgrid import DotGridWidget
from DotStar_Emulator.emulator.widgets.running_info import RunningInfo
from DotStar_Emulator.emulator.entities.dotgrid_select import DotGridSelect
from DotStar_Emulator.emulator.entities.running_fps import RunningFPS


class RunningScene(Scene):
    def __init__(self):
        super(RunningScene, self).__init__()

        self.draw_borders = config.get("DRAW_BORDERS")
        self.draw_indexes = config.get("DRAW_INDEXES")

        self.updated_txt = None
        self.led_grid_position_txt = None
        self.led_strip_index_txt = None
        self.led_value_txt = None
        self.led_color = None

        two_columns = panels.TwoColumns(config.get("EMU_RUNNING_MIN_RIGHT_COL_WIDTH"))
        self.set_panel(two_columns)

        self.dotgrid = DotGridWidget()
        two_columns.set_left(self.dotgrid)

        right = panels.TwoRows(40)
        two_columns.set_right(right)

        right.set_top(LogoWidget())

        right2 = panels.TwoRows(-60)
        right.set_bottom(right2)

        running_info = RunningInfo()
        right2.set_top(running_info)
        right2.set_bottom(self.bottom_right_panel())

        self.fit()

        select = DotGridSelect(self.dotgrid)
        self.add_entity(select)

        rect = running_info.emulator_fps_txt.layout.global_rect
        self.add_entity(RunningFPS(rect))

    def bottom_right_panel(self):
        """
        Bottom panel of the right side, menu / buttons.

        :return: gui Panel
        """

        panel = panels.TwoRows(16, use_surface=True, color=config.get("BRAND_BOX_BG"))
        panel.layout.margin.set(0, 5, 0, 5)

        text = TextLabelWidget("Menu", 10, (255, 227, 43))
        text.layout.margin.left = 4
        panel.set_top(text)

        bottom = panels.Grid(3, 2)
        bottom.layout.margin.set(0, 2, 2, 2)
        panel.set_bottom(bottom)

        # Buttons

        fps_button = ButtonWidget(self.fps_text(), key=pygame.K_f)
        bottom.set(fps_button, 0, 0)
        blinker.signal("gui.button.pressed").connect(self.on_fps, sender=fps_button)

        borders_button = ButtonWidget(self.draw_borders_text(), key=pygame.K_b)
        bottom.set(borders_button, 0, 1)
        blinker.signal("gui.button.pressed").connect(self.on_border, sender=borders_button)

        # edit_button = ButtonWidget("[E] Edit Grid", key=pygame.K_e)
        # bottom.set(edit_button, 2, 0)
        # blinker.signal("gui.button.pressed").connect(self.on_edit, sender=edit_button)

        edit_button = ButtonWidget(self.draw_indexes_text(), key=pygame.K_i)
        bottom.set(edit_button, 1, 0)
        blinker.signal("gui.button.pressed").connect(self.on_draw_indexes, sender=edit_button)

        exit_button = ButtonWidget("[X] Exit", key=pygame.K_x)
        bottom.set(exit_button, 2, 1)
        blinker.signal("gui.button.pressed").connect(self.on_exit, sender=exit_button, weak=True)

        about_button = ButtonWidget("[F1] About", key=pygame.K_F1)
        blinker.signal("gui.button.pressed").connect(self.on_about, sender=about_button, weak=True)
        bottom.set(about_button, 1, 1)

        return panel

    def on_edit(self, sender):
        """
        Callback for the Edit button pressed event.

        :param sender: blinker sender
        :return: None
        """

        # TODO debug function
        self.dotgrid.redraw()

    def draw_borders_text(self):
        """
        Helper function to get the text to be displayed on the button.

        :return: `str` with the correct button text based on the state of draw_borders
        """
        return "[B] Border {:.0f}".format(self.draw_borders)

    def on_border(self, sender):
        """
        Callback for the Draw border button pressed event.

        :param sender: blinker sender
        :return: None
        """

        # self.draw_borders = not self.draw_borders
        self.draw_borders += 1
        if self.draw_borders > len(config.get("DRAW_BORDERS_COLORS")):
            self.draw_borders = 0

        sender.text = self.draw_borders_text()
        sender.redraw()

        # Send signal to dotgrid to set the draw_borders
        blinker.signal("dotgrid.drawborders").send(None, draw_borders=self.draw_borders)

    def draw_indexes_text(self):
        """
        Helper function to get the text to be displayed on the button.

        :return: `str` with the correct button text based on the state of draw_borders
        """

        return "[I] Indexes {:.0f}".format(self.draw_indexes)

    def on_draw_indexes(self, sender):
        """
        Callback for the Draw Indexes button pressed event.

        :param sender: blinker sender
        :return: None
        """

        self.draw_indexes += 1
        if self.draw_indexes > len(config.get("DRAW_INDEXES_COLORS")):
            self.draw_indexes = 0
        sender.text = self.draw_indexes_text()
        sender.redraw()

        # Send signal to dotgrid to set the draw_indexes
        blinker.signal("dotgrid.drawindexes").send(None, draw_indexes=self.draw_indexes)

    @staticmethod
    def fps_text():
        """
        Helper function to get the text to be displayed on the FPS button.

        :return: `str` with the correct button text based on the state of the app.fps_limit
        """

        return "[F] FPS {}".format(globals.current_app.fps_limit if globals.current_app.fps_limit <= 60 else "...")

    def on_fps(self, sender):
        """
        Callback for the FPS button pressed event

        :param sender: blinker sender
        :return: None
        """

        if globals.current_app.fps_limit == 10:
            blinker.signal("app.fps").send(None, fps=2000)
        elif globals.current_app.fps_limit == 2000:
            blinker.signal("app.fps").send(None, fps=60)
        elif globals.current_app.fps_limit == 60:
            blinker.signal("app.fps").send(None, fps=30)
        else:
            blinker.signal("app.fps").send(None, fps=10)

        sender.text = self.fps_text()

    def on_exit(self, sender):
        """
        Callback for the Exit button pressed event

        :param sender: blinker sender
        :return: None
        """
        blinker.signal("app.exit").send(None)

    def on_about(self, sender):
        """
        Callback for the About button pressed event

        :param sender: blinker sender
        :return: None
        """
        blinker.signal("app.setscene").send(None, scene_name="about")
