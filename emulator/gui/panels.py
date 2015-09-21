from pygame.math import Vector2

from .widget import Widget
from .flags import *

__all__ = ["SizedRows", "TwoColumns", "Grid", "TwoRows", "BasePanel"]


class BasePanel(Widget):

    def __init__(self, use_surface=False, color=None):
        """
        Base class for a panel.  A panel is a widget that has children widgets, and lays them out according to
        a pattern determined by the panel.

        If BasePanel.use_surface=True, then the surface of the panel will be filled with the given color.

        Panels that do not have BasePanel.use_surface set, do not use use the render function of the base Widget at
        all, and instead pass along the offsets and surface during the on_draw call to have its children widgets
        render to the parent surface directly.  Most panels will be used in this manner, as they are typically
        blindly used for layout only.

        BasePanel does not do any layout/fit of its children widgets, so it must be subclassed.

        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """

        super(BasePanel, self).__init__(use_surface=use_surface)

        self._widgets = []  # store the children widgets
        self.color = color if color else (0, 0, 0)  # default color of black

    def add_widget(self, widget):
        """
        Add the widget to the panel, and call the Widget.set_redraw_callback for this BasePanel.redraw function to
        be called when the Widget is made dirty.

        :param widget: any object derived from `gui.widget.Widget`. So a Raw Widget or a panel are permitted.
        :return: None
        """

        self._widgets.append(widget)
        widget.set_redraw_callback(self.redraw)

    def on_render(self):
        """
        When the BasePanel.use_surface is set, this will render the children widgets to the BasePanel.surface.

        :return: None
        """

        self.surface.fill(self.color)

        for widget in self._widgets:
            # pass g_offset of 0, 0 because we are rendering to this BasePanel.surface, so there is no global offset
            # to worry about.
            widget.on_draw(self.surface, Vector2(0, 0))

    def update(self, elapsed):
        for widget in self._widgets:
            widget.update(elapsed)

    def on_draw(self, surface, g_offset):
        """
        If on BasePanel.use_surface is false, then pass along the surface and global_offsets + total_offset of the
        BasePanel to the children so they can draw themselves to the parent surface.

        :param surface: pygame.Surface
        :param g_offset: pygame.math.Vector2 of the offset to be added to the widgets offsets during render / drawing.
        :return: None
        """
        if self.use_surface:
            super(BasePanel, self).on_draw(surface, g_offset)
        else:
            for widget in self._widgets:
                widget.on_draw(surface, self.layout.total_offset + g_offset)


class TwoColumns(BasePanel):

    def __init__(self, x, use_surface=False, color=None):
        """
        Simple panel with two children widgets.  One to the Left and one to the Right defined by y.

        Examples of the layout, of a (200px, 100px) TwoColumns Panel
        x = 50
            left size = (50px, 100px)
            left offset = (0px, 0px)
            right size = (150px, 100px)
            right offset (50px, 0px)
        y = -25
            left size = (175px, 200px)
            left offset = (0px, 0px)
            right size = (25px, 200px)
            right offset (175px, 0px)
        y = "10%"
            left size = (20px, 200px)
            left offset = (0px, 0px)
            right size = (180px, 200px)
            right offset (20px, 0px)
        y = "-10%"
            left size = (180px, 200px)
            left offset = (0px, 0px)
            right size = (20px, 200px)
            right offset (180px, 0px)

        :param x:   integer can be positive or negative number. Positive x will set row x pixels from Left Side
                    Negative y will set row back x pixels from Right Side. Can also be set in positive or
                    negative percentages as strings "-10%" or "10%"
        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """

        super(TwoColumns, self).__init__(use_surface=use_surface, color=color)

        # store requested_x separate from calculated x because requested x may be a string and we want to keep
        # reference to it.  If its a percentage, we can't actually determine x until fit is called.
        self.requested_x = x
        self.x = 0

        # Refernce to the left and right widgets
        self.left = None
        self.right = None

    def fit(self, possible_size, offset, global_offset, flags):
        super(TwoColumns, self).fit(possible_size, offset, global_offset, flags)
        w_global_offset = global_offset + self.layout.total_offset

        # Determine the position of column split, defined as x
        if type(self.requested_x) == str:
            # Convert string to float
            if self.requested_x.endswith("%"):
                p = (float(self.requested_x[:-1]) / 100.0)
                # negative percentage, so column is defined form the right side
                if self.requested_x.startswith("-"):
                    p += 1
                self.x = p * self.layout.size.x
            else:
                raise AttributeError("invalid x argument")
        else:
            self.x = self.requested_x

        if self.left:
            if self.x > 0:
                size = Vector2(self.x, self.layout.size.y)
            else:
                size = Vector2(self.layout.size.x + self.x, self.layout.size.y)
            offset = Vector2(0, 0)
            self.left.fit(size, offset, w_global_offset, FILLX | FILLY)

        if self.right:
            if self.x > 0:
                size = Vector2(self.layout.size.x - self.x, self.layout.size.y)
                offset = Vector2(self.x, 0)
            else:
                size = Vector2(self.x * -1, self.layout.size.y)
                offset = Vector2(self.layout.size.x + self.x, 0)
            self.right.fit(size, offset, w_global_offset, FILLX | FILLY)

    def set_left(self, widget):
        """
        Set and store the left widget.

        :param widget: any class derived from gui.widget.Widget
        :return: None
        """

        # if self.left:
        #     del self._widgets[widget]

        self.left = widget
        self.add_widget(widget)

    def set_right(self, widget):
        """
        Set and store the right widget.

        :param widget: any class derived from gui.widget.Widget
        :return: None
        """

        # if self.right:
        #     del self._widgets[widget]

        self.right = widget
        self.add_widget(widget)


class TwoRows(BasePanel):

    def __init__(self, y, use_surface=False, color=None):
        """
        Simple panel with two children widgets.  One on top of the other defined by y.

        Examples of the layout, of a (100px, 200px) TwoRows Panel
        y = 50
            top size = (100px, 50px)
            top offset = (0px, 0px)
            bottom size = (100px, 150px)
            bottom offset (0px, 50px)
        y = -25
            top size = (100px, 175px)
            top offset = (0px, 0px)
            bottom size = (100px, 25px)
            bottom offset (0px, 175px)
        y = "10%"
            top size = (100px, 20px)
            top offset = (0px, 0px)
            bottom size = (100px, 180px)
            bottom offset (0px, 20px)
        y = "-10%"
            top size = (100px, 180px)
            top offset = (0px, 0px)
            bottom size = (100px, 20px)
            bottom offset (0px, 180px)

        :param y:   integer can be positive or negative number. Positive y will set column y pixels from Top Side
                    Negative y will set column back y pixels from Bottom Side. Can also be set in positive or
                    negative percentages as strings "-10%" or "10%"
        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """

        super(TwoRows, self).__init__(use_surface=use_surface, color=color)

        # store requested_y separate from calculated x because requested y may be a string and we want to keep
        # reference to it.  If its a percentage, we can't actually determine y until fit is called.
        self.y = 0
        self.requested_y = y

        self.top = None
        self.bottom = None

    def fit(self, possible_size, offset, global_offset, flags):
        super(TwoRows, self).fit(possible_size, offset, global_offset, flags)
        w_global_offset = global_offset + self.layout.total_offset

        # Determine the position of row split, defined as y
        if type(self.requested_y) == str:
            # Convert string to float
            if self.requested_y.endswith("%"):
                p = (float(self.requested_y[:-1]) / 100.0)
                # negative percentage, so row is defined form the bottom side
                if self.requested_y.startswith("-"):
                    p += 1
                self.y = p * self.layout.size.y
            else:
                raise AttributeError("invalid x argument")
        else:
            self.y = self.requested_y

        if self.top:
            if self.y > 0:
                size = Vector2(self.layout.size.x, self.y)
            else:
                size = Vector2(self.layout.size.x, self.layout.size.y + self.y)

            offset = Vector2(0, 0)
            self.top.fit(size, offset, w_global_offset, FILLX | FILLY)

        if self.bottom:
            if self.y > 0:
                size = Vector2(self.layout.size.x, self.layout.size.y - self.y)
                offset = Vector2(0, self.y)
            else:
                size = Vector2(self.layout.size.x, self.y * -1)
                offset = Vector2(0, self.layout.size.y + self.y)

            self.bottom.fit(size, offset, w_global_offset, FILLX | FILLY)

    def set_top(self, widget):
        """
        set and store the top widget.

        :param widget: any class derived from gui.widget.Widget
        :return: None
        """

        # if self.top:
        #     del self._widgets[widget]

        self.top = widget
        self.add_widget(widget)

    def set_bottom(self, widget):
        """
        Set and store the bottom widget.

        :param widget: any class derived from gui.widget.Widget
        :return: None
        """

        # if self.bottom:
        #     del self._widgets[widget]

        self.bottom = widget

        self.add_widget(widget)


class Grid(BasePanel):
    def __init__(self, x, y, use_surface=False, color=None):
        """
        A panel that is equally divided into a x number of columns and y number of rows.  The size of the cell
        is simply determined by the size of the Grid.layout.size / (x, y)

        The default fit is to have the children widgets fill out in both the x and y directions.

        :param x: number of columns to divide the panel into
        :param y: number of rows to divide the panel into
        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """
        super(Grid, self).__init__(use_surface=use_surface, color=color)
        self.x = x  # number of columns
        self.y = y  # number of rows

    def fit(self, possible_size, offset, global_offset, flags):
        super(Grid, self).fit(possible_size, offset, global_offset, flags)
        w_global_offset = global_offset + self.layout.total_offset

        for widget in self._widgets:
            width = self.layout.size.x / self.x
            height = self.layout.size.y / self.y
            size = Vector2(width, height)

            offset_x = width * widget.layout.data['x']
            offset_y = height * widget.layout.data['y']
            offset = Vector2(offset_x, offset_y)

            widget.fit(size, offset, w_global_offset, FILLX | FILLY)

    def set(self, widget, x, y):
        """
        Set the widget in place, no bounds checks are performed, so if it is out of range, it will not
        render properly.

        :param widget: any class derived from gui.widget.Widget
        :param x:
        :param y:
        :return:
        """

        # store data on the widget layout class so we know what position it is in the grid during the fit call.
        widget.layout.data['x'] = x
        widget.layout.data['y'] = y

        self.add_widget(widget)


class SizedRows(BasePanel):
    def __init__(self, y, use_surface=False, color=None):
        """
        A panel that arranges its children in a single column. Each row in the columns is spaced exactly y pixels.

        :param y: pixel size of each row in the column
        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """

        super(SizedRows, self).__init__(use_surface=use_surface, color=color)
        self.y = y

    def fit(self, possible_size, offset, global_offset, flags):
        super(SizedRows, self).fit(possible_size, offset, global_offset, flags)
        w_global_offset = global_offset + self.layout.total_offset

        for widget in self._widgets:
            width = self.layout.size.x
            height = self.y
            size = Vector2(width, height)

            offset_x = 0
            offset_y = height * widget.layout.data['y']
            offset = Vector2(offset_x, offset_y)

            widget.fit(size, offset, w_global_offset, FILLX | FILLY)

    def set(self, widget, y):
        """

        Care must be taken as no checks are performed that the y Row will actually fit into the SizedRows.layout.size.
        So, if y * self.y is larger than the size of the SizedRow, it will not be properly rendered.

        :param widget: any class derived from gui.widget.Widget
        :param y: index of the row the widget should be laid out to.
        :return: None
        """

        # store data on the widget layout class so we know what row it is during fitting.
        widget.layout.data['y'] = y
        self.add_widget(widget)


class CenterSingle(BasePanel):

    def __init__(self, use_surface=False, color=None):
        """
        A panel that arranges a single sized widget in the center of itself.

        :param use_surface: `bool`, default=True, use a surface to render the widget
        :param color: (r, g, b) or (r, g, b, a) or pygame.Color
        :return:
        """

        super(CenterSingle, self).__init__(use_surface=use_surface, color=color)

        self.widget = None

    def fit(self, possible_size, offset, global_offset, flags):
        super(CenterSingle, self).fit(possible_size, offset, global_offset, flags)
        w_global_offset = global_offset + self.layout.total_offset

        for widget in self._widgets:
            # width = self.layout.size.x
            # height = self.y
            # size = Vector2(width, height)
            size = self.layout.size

            offset_x = 0
            offset_y = 0
            offset = Vector2(offset_x, offset_y)

            widget.fit(size, offset, w_global_offset, CENTERX | CENTERY)

    def set(self, widget):
        """

        :param widget: any class derived from gui.widget.Widget
        :return: None
        """

        self.add_widget(widget)
