from DotStar_Emulator.emulator.gui import widget
from DotStar_Emulator.emulator import globals, config


class LogoWidget(widget.Widget):

    def __init__(self, use_surface=True):
        """
        Widget for display the emulator apps logo

        :param use_surface: `Boolean` Use widget surface
        :return:
        """

        super(LogoWidget, self).__init__(use_surface=use_surface)

        self.layout.margin.set(0, 5, 10, 5)

    def on_render(self):
        self.surface.fill(config.get("BRAND_BOX_BG"))

        font = globals.current_app.get_font(22)

        c = config.get("BRAND_TITLE")
        text, text_pos = font.render(config.get("WINDOW_CAPTION"), c)
        text_pos.center = self.surface.get_rect().center
        self.surface.blit(text, text_pos)

