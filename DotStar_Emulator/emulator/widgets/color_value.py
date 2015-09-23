from DotStar_Emulator.emulator.gui import Widget


class ColorValueWidget(Widget):

    def __init__(self, color, use_surface=True):
        """
        Simple Widget that just fills itself with the assigned Color

        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :param use_surface: `Boolean` Use widget surface
        :return:
        """

        super(ColorValueWidget, self).__init__(use_surface=use_surface)

        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        """
        :param value: (r, g, b) or (r, g, b, a) or pygame.Color
        :return: None
        """

        self._color = value
        self.redraw()

    def on_render(self):
        """
        Just simply fill the Widgets surface with the assigned color
        :return:
        """

        self.surface.fill(self._color)
