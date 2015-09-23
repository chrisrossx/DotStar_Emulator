import blinker
from pygame.math import Vector2

from DotStar_Emulator.emulator import config
from DotStar_Emulator.emulator import globals
from DotStar_Emulator.emulator.gui import TwoColumns, SizedRows, TextLabelWidget
from .color_value import ColorValueWidget


class RunningInfo(TwoColumns):
    def __init__(self):
        """
        Widget to show information about the running screen.

        :return:
        """
        super(RunningInfo, self).__init__(x=145)
        self.layout.margin.set(0, 5, 10, 5)

        # LED information widgets
        self.led_grid_position_txt = []  # value of grid position
        self.led_strip_index_txt = []  # value of strip index
        self.led_value_txt = []  # value of strip index color
        self.led_color = []  # widget to show color block of strip index color

        row_size = 14
        left = SizedRows(row_size)
        right = SizedRows(row_size)
        self.set_left(left)
        self.set_right(right)

        left.set(self.hd_txt("Information"), 0)

        i = 1
        left.set(self.lbl_text("Emulator FPS:"), i)
        self.emulator_fps_txt = self.val_text("")
        right.set(self.emulator_fps_txt, i)

        i += 1
        left.set(self.lbl_text("Grid size:"), i)
        grid_size = Vector2(config.get("GRID_SIZE"))
        pixel_count = globals.mapping_data.pixel_count
        self.grid_size_txt = self.val_text("({:.0f}, {:.0f}), {:.0f}".format(grid_size.x, grid_size.y, pixel_count))
        right.set(self.grid_size_txt, i)

        i += 1
        left.set(self.lbl_text("Packet Updated:"), i)
        self.packet_updated_txt = self.val_text("")
        right.set(self.packet_updated_txt, i)

        i += 1
        left.set(self.lbl_text("Packet length:"), i)
        self.packet_length_txt = self.val_text("")
        right.set(self.packet_length_txt, i)

        i += 1
        left.set(self.lbl_text("Packet Rate:"), i)
        self.packet_rate = self.val_text("")
        right.set(self.packet_rate, i)

        i += 2
        self.pixel_info_count = 4
        self.create_pixel_info(left, right, i)

        blinker.signal("dotgrid.select.set").connect(self.on_dotgrid_select_set)
        blinker.signal("stripdata.updated").connect(self.on_data_updated)
        blinker.signal("ratecounter.updated").connect(self.on_ratecounter_updated)

    def on_ratecounter_updated(self, sender, count):
        """
        Event callback when the rate_counter updates the frequency count

        :param sender: blinker sender
        :param count: current frequency count in Hz
        :return: None
        """

        self.packet_rate.text = "{} Hz".format(count)
        self.redraw()

    def on_data_updated(self, sender):
        """
        Event callback when the strip_data has received updated data

        :param sender: blinker sender
        :return: None
        """
        try:
            self.packet_updated_txt.text = globals.strip_data.updated.strftime("%H:%M:%S.%f")

            packet_length = "{} bytes".format(globals.strip_data.packet_length)
            self.packet_length_txt.text = packet_length
        except:
            pass

        for i in range(self.pixel_info_count):

            try:
                index = int(self.led_strip_index_txt[i].text)
                c, b, g, r = globals.strip_data.get(index)
                self.led_value_txt[i].text = "({}, {}, {})".format(r, g, b)
                self.led_color[i].color = (r, g, b, 0)
            except ValueError:
                continue

        self.redraw()

    @staticmethod
    def hd_txt(text):
        """
        Shortcut to return a TextLabelWidget styled for a text header

        :param text: `str` with the text to be rendered
        :return: gui.text.TextLabelWidget
        """

        return TextLabelWidget(text, 10, (255, 227, 43))

    @staticmethod
    def lbl_text(text):
        """
        Shortcut to return a TextLabelWidget styled for a label

        :param text: `str` with the text to be rendered
        :return: gui.text.TextLabelWidget
        """

        return TextLabelWidget(text, 13, (185, 185, 185))

    @staticmethod
    def val_text(text):
        """
        Shortcut to return a TextLabelWidget styled for a value

        :param text: `str` with the text to be rendered
        :return: gui.text.TextLabelWidget
        """

        return TextLabelWidget(text, 13, (255, 255, 255))

    def create_pixel_info(self, left, right, offset):

        for i in range(self.pixel_info_count):
            led_grid_position_txt = self.val_text("")
            led_strip_index_txt = self.val_text("")
            led_value_txt = self.val_text("")
            led_color = ColorValueWidget((0, 0, 0, 0))
            # led_color.layout.margin.set(4, 0, 0, 0)
            self.led_grid_position_txt.append(led_grid_position_txt)
            self.led_strip_index_txt.append(led_strip_index_txt)
            self.led_value_txt.append(led_value_txt)
            self.led_color.append(led_color)

            row = (i * 5) + (offset + 1)
            right.set(led_grid_position_txt, row + 1)
            right.set(led_strip_index_txt, row + 0)

            value_panel = TwoColumns(-14)
            value_panel.set_left(led_value_txt)
            value_panel.set_right(led_color)

            right.set(value_panel, row + 2)
            # right.set(led_value_txt, row + 2)
            # right.set(led_color, row + 3)

            row = (i * 5) + offset
            if i == 0:
                left.set(self.hd_txt("Selected LED:"), row)
            else:
                left.set(self.hd_txt("Prev Selected LED {}:".format(i + 1)), row)
            left.set(self.lbl_text("Grid Position:"), row + 2)
            left.set(self.lbl_text("LED Strip Index:"), row + 1)
            left.set(self.lbl_text("Value:"), row + 3)

    def on_dotgrid_select_set(self, sender, x, y):

        for i in range(self.pixel_info_count - 1, 0, -1):

            self.led_grid_position_txt[i].text = self.led_grid_position_txt[i - 1].text
            self.led_value_txt[i].text = self.led_value_txt[i - 1].text
            self.led_strip_index_txt[i].text = self.led_strip_index_txt[i - 1].text
            self.led_color[i].color = self.led_color[i - 1].color

        index = globals.mapping_data.data[x][y]
        c, b, g, r = globals.strip_data.get(index)

        self.led_grid_position_txt[0].text = "({}, {})".format(x, y)
        self.led_strip_index_txt[0].text = "{}".format(index)
        self.led_value_txt[0].text = "({}, {}, {})".format(r, g, b)
        self.led_color[0].color = (r, g, b, 0)

    pass
