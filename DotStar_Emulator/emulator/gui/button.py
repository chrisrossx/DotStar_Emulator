import pygame
import blinker

from DotStar_Emulator.emulator import globals
from .widget import Widget

__all__ = ["ButtonWidget", ]


class ButtonWidget(Widget):
    def __init__(self, text, key=None):
        """
        Simple Button Widget that allows a shortcut key.  The button will show hover effect with a mouse and also
        activates when clicked.

        When clicked or keypressed, a blinker event 'gui.button.pressed' will fire, withe the button instance as the
        sender.

        :param text: Text to display on the button.
        :param key: default=None, a pygame key constant.
        :return:
        """

        super(ButtonWidget, self).__init__()
        self.layout.margin.set(2, 2, 2, 2)
        self._text = text
        self.key = key

        # Keep track of which button state to display, highlight=hover.
        self.highlight = False

        blinker.signal("event.mousebuttondown").connect(self.on_mousebuttondown)
        blinker.signal("event.mousemotion").connect(self.on_mousemotion)

        if self.key:
            blinker.signal("event.keydown").connect(self.on_keydown, sender=self.key)

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

    def on_keydown(self, sender, event):
        """
        The button shortcut key was pressed.
        Send blinker "gui.button.pressed" event with this button instance as sender.

        :param sender:
        :param event: pygame.event instance
        :return: None
        """

        blinker.signal("gui.button.pressed").send(self)

    def on_mousebuttondown(self, sender, event):
        """
        Mouse button was clicked, if it was clicked on the button then
        Send blinker "gui.button.pressed" event with this button instance as sender.

        :param sender:
        :param event: pygame.event instance
        :return: None
        """

        if self.layout.global_rect.collidepoint(event.pos[0], event.pos[1]):
            blinker.signal("gui.button.pressed").send(self)

    def on_mousemotion(self, sender, event):
        """
        Callback for the app/pygame mousemotion event.  If the mouse cursor is over the button then redraw the
        button in a hover state.

        :param sender: blinker sender reference
        :param event: pygame.event instance
        :return: None
        """

        if self.layout.global_rect.collidepoint(event.pos[0], event.pos[1]):
            if not self.highlight:
                self.highlight = True
                self.redraw()
        else:
            if self.highlight:
                self.highlight = False
                self.redraw()

    def on_render(self):
        if self.highlight:
            self.surface.fill((82, 185, 212))
        else:
            self.surface.fill((33, 150, 214))

        rect = self.surface.get_rect()
        for i in [1, 2]:
            c = (2, 90, 146)
            s = (0, rect.bottom-i)
            e = (rect.right, rect.bottom-i)
            pygame.draw.line(self.surface, c, s, e)

        font = globals.current_app.get_font(10)

        c = (255, 255, 255)
        text, text_pos = font.render(self._text, c)
        text_pos.centery = self.surface.get_rect().centery - 1
        text_pos.left = 4
        self.surface.blit(text, text_pos)
