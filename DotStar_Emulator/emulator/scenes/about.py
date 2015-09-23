import os

import blinker
import pygame
from pygame.math import Vector2

from DotStar_Emulator.emulator import config
from DotStar_Emulator.emulator.scene import Scene
from DotStar_Emulator.emulator.gui import panels
from DotStar_Emulator.emulator.gui import TextLabelWidget, ButtonWidget
from DotStar_Emulator.emulator.utils import MEDIA_PATH


class AboutScene(Scene):
    def __init__(self):
        super(AboutScene, self).__init__()

        two_rows = panels.TwoRows(-50)
        self.set_panel(two_rows)

        top = self.text_panel()

        two_rows.set_top(top)

        bottom = panels.CenterSingle()
        two_rows.set_bottom(bottom)

        button = ButtonWidget("[F1] Return", key=pygame.K_F1)
        button.layout.requested_size = Vector2(100, 21)
        bottom.set(button)
        blinker.signal("gui.button.pressed").connect(self.on_return, sender=button)

        self.fit()

    @staticmethod
    def text_panel():
        panel = panels.CenterSingle(25)

        rows_panel = panels.SizedRows(18, use_surface=True, color=(40, 40, 40))
        rows_panel.layout.requested_size = Vector2(500, 400)
        panel.set(rows_panel)

        filename = os.path.join(MEDIA_PATH, 'about.txt')
        with open(filename, 'r') as f:
            text = f.read()

        text_split = text.split("\n")

        widget = TextLabelWidget(config.get("WINDOW_CAPTION"), 18, config.get("BRAND_TITLE"))
        widget.layout.margin.set(0, 0, 0, 5)
        rows_panel.set(widget, 0)

        for i, line in enumerate(text_split):
            widget = TextLabelWidget(line, 12, (255, 255, 255))
            widget.layout.margin.set(0, 0, 0, 5)
            rows_panel.set(widget, i+2)

        return panel

    @staticmethod
    def on_return(sender):
        blinker.signal("app.setscene").send(None, scene_name="running")
