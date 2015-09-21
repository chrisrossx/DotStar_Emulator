from __future__ import print_function

from DotStar_Emulator.emulator import current_app
from DotStar_Emulator.emulator.entity import Entity
from DotStar_Emulator.emulator import config


class RunningFPS(Entity):
    def __init__(self, rect):
        """
        Entity to draw the FPS value to the screen. This is an entity, so that it can be updated at a high rate
        without redrawing the entire GUI.

        :param rect: pygame.Rect on where the FPS should be drawn.
        :return:
        """
        super(RunningFPS, self).__init__()
        self.rect = rect

        self.font = current_app.get_font(13)
        self.text = None
        self.text_pos = None
        self.update_rate = config.get("FPS_UPDATE_RATE")
        self.elapsed = self.update_rate + 1

    def update(self, elapsed):
        """
        Update the FPS text at specified rate.

        :param elapsed: milliseconds og pygame clock since last call
        :return: None
        """

        self.elapsed += elapsed
        if self.elapsed > self.update_rate:
            self.text, self.text_pos = self.font.render("{:.0f}".format(current_app.clock.get_fps()), (255, 255, 255))
            self.text_pos.centery = self.rect.centery
            self.text_pos.left = self.rect.left
            self.elapsed = 0

    def on_draw_after(self, surface):
        """
        Draw the FPS text ontop of the gui

        :param surface: surface to blit the Widget.surface to.
        :return: None
        """

        surface.blit(self.text, self.text_pos)
