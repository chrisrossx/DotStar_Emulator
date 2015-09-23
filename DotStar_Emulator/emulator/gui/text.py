import pygame

from DotStar_Emulator.emulator import current_app
from .widget import Widget
from .flags import *

__all__ = ["TextLabelWidget", ]


class TextLabelWidget(Widget):
    def __init__(self, text, font_size, color, flags=CENTERY):
        """
        A Text Label gui widget. Simply renders text.

        TextLabelWidget pulls fonts from the current_app.get_font
        method.

        :param text: the string of text to be rendered.
        :param font_size: pixel size of the font.
        :param color: (r, g, b) or (r, g, b, a)
        :param flags: flags to indicate how the text should be blited to the Widget.surface. default=CENTERY
        :return:
        """
        super(TextLabelWidget, self).__init__(use_surface=True)

        # Render the widget surface as transparent by default.
        self.surface_flags = pygame.SRCALPHA

        self._text = text
        self.color = color
        self.size = font_size
        self.flags = flags

    @property
    def text(self):
        """
        :return: the stored text that is being displayed.
        """
        return self._text

    @text.setter
    def text(self, value):
        """
        Sets the text and notifies the widget to redraw.

        :param value: text to render
        :return: None
        """

        self._text = value
        self.redraw()

    def on_render(self):
        """
        Render the text to the Widget.surface and position it based on TextLabelWidget.flags

        :return: None
        """

        self.surface.fill((0, 0, 0, 0))

        font = current_app.get_font(self.size)

        text, text_pos = font.render(self._text, self.color)
        if self.flags & CENTERX:
            text_pos.centerx = self.surface.get_rect().centerx
        else:
            text_pos.left = 0

        if self.flags & CENTERY:
            text_pos.centery = self.surface.get_rect().centery
        else:
            text_pos.top = 0

        self.surface.blit(text, text_pos)
