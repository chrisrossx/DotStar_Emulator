import random

import pygame
from pygame.math import Vector2
from pygame import Rect

from .flags import *

__all__ = ["Widget", ]


class Margin(object):

    def __init__(self, top=None, right=None, bottom=None, left=None):
        """
        Stores information about the Widget Styles margins.

        :param top: top margin in pixels, default = 0
        :param right: right margin in pixels, default = 0
        :param bottom: left margin in pixels, default = 0
        :param left: left margin in pixels, default = 0
        :return: None
        """

        self.top = top if top else 0
        self.bottom = bottom if bottom else 0
        self.left = left if left else 0
        self.right = right if right else 0

    def set(self, top, right, bottom, left):
        """
        Set the margins. Order is in css fashion for reasons of insanity.

        :param top: top margin in pixels
        :param right: right margin in pixels
        :param bottom: left margin in pixels
        :param left: left margin in pixels
        :return: None
        """

        if top:
            self.top = top
        if right:
            self.right = right
        if bottom:
            self.bottom = bottom
        if left:
            self.left = left

    @property
    def topleft(self):
        """
        Return a Vector2 class of the top left corner margins
        :return: 'class pygame.math.Vector2' Vector2(left, top)
        """
        return Vector2(self.left, self.top)

    @property
    def widthheight(self):
        """
        Return a Vector2 class of the total combined margins for width and height.
        width is left + right margins.
        height is top + bottom margins.

        :return: 'class pygame.math.Vector2' Vector2(width, height)
        """

        return Vector2(self.left + self.right, self.top + self.bottom)


class WidgetLayout(object):
    def __init__(self):
        """
        Manage the widgets layout.
        :return:
        """

        # Widgets are automatically sized by its parent panel(widget).  self.requested_size can influence that
        # automatic sizing.
        self.requested_size = Vector2(0, 0)

        # The size of the drawable widget. Does not include margins.
        self.size = Vector2(0, 0)
        # Offset of this widgets location within it's parents panel(widget) surface.
        # Does not include its own margins. use self.total_offset to include margins
        self.offset = Vector2(0, 0)
        # pygame.Rect, ( total_offset.x, total_offset.y, size.x, size.y)
        self.rect = Rect(0, 0, 0, 0)
        # base global_offset of the widget in screen space. would still need to add this widgets total_offset to get
        # correct screen space.
        self.base_global_offset = Vector2(0, 0)
        # pygame.Rect, with global_offset + total_offset for position, and self.size for width, height.
        self.global_rect = Rect(0, 0, 0, 0)
        # Information about the styles margins.
        self.margin = Margin()
        # data used during fit, which can be set by parent panel(widget). Useful so parent panel doesn't have to have
        # its own way of storing information about the widget for automatic layout. Such as grid x, y position.
        self.data = {}

    @property
    def total_offset(self):
        """
        :return: 'class pygame.math.Vector2' total offset of this widgets position within its parents surface.
        """
        return self.margin.topleft + self.offset

    # @property
    # def total_size(self):
    #     """
    #
    #     :return: ;class pygame.math.Vector2' total width including margins
    #     """
    #     return self.size + self.margin.widthheight

    def set_size(self, possible_size, offset, global_offset, flags):
        """
        Automatically calculate the widgets size and position.  Size will never exceed possible_size, but may be
        smaller depending on flags.  The calculation is also influenced by the widgets self.requested_size

        FILLX
        FILLY
        CENTERX
        CENTERY

        :param possible_size: Vector2 of the maximum size the parent panel(widget) has allotted this widget.
        :param offset:  Vector2 top left corner of where this widget will draw n the parent's surface
        :param global_offset: total screen global offset of where offset is actually located. This is needed for
                              to maintain screen space rect's of this widget. useful for mouse clicks..
        :param flags: Positioning flags to influence the automatic fitting.
        :return: None
        """

        # Store base global_offset
        self.base_global_offset = global_offset
        # Store base offset
        self.offset = offset

        size = Vector2(0, 0)

        if flags & FILLX:
            if self.requested_size.x == 0 or self.requested_size.x == -1:
                size.x = possible_size.x
            else:
                raise Exception("can not FILLX, as widget.style.x is already set")
        else:
            if self.requested_size.x == 0:
                raise Exception("widget.style.x is equal to 0")
            elif self.requested_size.x == -1:
                # even if FILLX wasn't set by parent, fill out to parents possible_size
                size.x = possible_size.x
            else:
                size.x = self.requested_size.x

        if flags & FILLY:
            if self.requested_size.y == 0 or self.requested_size.y == -1:
                size.y = possible_size.y
            else:
                raise Exception("can not FILLY, as widget.style.y is already set")
        else:
            if self.requested_size.y == 0:
                raise Exception("widget.style.y is equal to 0")
            elif self.requested_size.y == -1:
                # even if FILLY wasn't set by parent, fill out to parents possible_size
                size.y = possible_size.y
            else:
                size.y = self.requested_size.y

        # because size is the size of the widget's drawable surface, remove its own margins.
        size -= self.margin.widthheight
        self.size = size

        # Once widgets size has been determined, we can center it within its parents space by adjusting the margins.
        # TODO this will not work if the widgets are ever re-sized, as the margins are used to calculate the size in the
        # step just above this.
        if flags & CENTERX:
            space = possible_size.x - size.x
            self.margin.left = space / 2.0
            self.margin.right = space / 2.0
        if flags & CENTERY:
            space = possible_size.y - size.y
            self.margin.top = space / 2.0
            self.margin.bottom = space / 2.0

        # Cache Rectangle, topleft is offset + margin, size is size of drawable widget surface.
        self.rect = Rect(self.total_offset, self.size)

        # Cache Global Rect. Same as above but globally positioned. Useful for mouse events
        self.global_rect = Rect(self.base_global_offset + self.total_offset, self.size)


class Widget(object):

    def __init__(self, use_surface=True):
        """
        A gui entity that can render itself to its own surface, and then draw that surface to a parent when
        called to do so.

        if use_surface is false, then the widget will not render it self to its own surface.  But on_draw can be
        used to draw anything directly to the parent.

        The widget keeps track if it is dirty, and will only render itself if its dirty on a on_draw call.  use
        Widget.redraw() to notify if the widget is dirty. Simply setting Widget._dirty = True will not work, as that
        would not notify the parent, and most likely Widget.on_draw will never be called.

        :param use_surface: `bool`, default=True, use a surface to render the widget
        :return:
        """

        self.debug_draw = False

        self.layout = WidgetLayout()

        self._dirty = True  # does the widget need to render itself?
        self.use_surface = use_surface  # does the widget use a surface to render it self to?
        self._redraw_callback = None  # stored function to call alongside self.redraw

        self.surface = None  # pygame surface for drawing the Widget too.
        self.surface_flags = 0  # flags that are passed to pygmae.Surface when creating

    def update(self, elapsed):
        """
        Called every game loop iteration independently of any draw or render requests.

        :param elapsed: milliseconds og pygame clock since last call
        :return: None
        """

    def set_redraw_callback(self, callback):
        """
        When a widget becomes dirty, the widget needs to tell its parent widget that the it is dirty.
        Widget.redraw() will call this function if it is set.

        :param callback: function
        :return: None
        """

        self._redraw_callback = callback

    def redraw(self):
        """
        Set the widget as dirty, so next on_draw call will call render.  Also notify parent if redraw_callback is set.

        :return: None
        """

        self._dirty = True
        if self._redraw_callback:
            self._redraw_callback()

    def render(self):
        """
        Start to render the widget to its own Widget.Surface.  This function will first create the surface if
        needed.  The it will call Widget.on_render, which is the method that should be overridden by a subclass.
        Then it will mark the Widget as no longer being dirty.

        :return: None
        """
        if not self.surface:
            self.surface = pygame.Surface(self.layout.size, self.surface_flags)

        self.on_render()
        self._dirty = False

    def fit(self, possible_size, offset, global_offset, flags):
        """
        Start to size the panel, this is almost an alias for WidgetStyle.set_size, but allows for the
        subsequent calling of Widget.on_fit.  Some widgets need to be notified when a widget has been
        sized.

        :param possible_size: Vector2 of the maximum size the parent panel(widget) has allotted this widget.
        :param offset:  Vector2 top left corner of where this widget will draw n the parent's surface
        :param global_offset: total screen global offset of where offset is actually located. This is needed for
                              to maintain screen space rect's of this widget. useful for mouse clicks..
        :param flags: Positioning flags to influence the automatic fitting.

        :return: None
        """
        self.layout.set_size(possible_size, offset, global_offset, flags)
        self.on_fit()

    def on_fit(self):
        """
        Called after a widget has been fit/sized.

        :return: None
        """

        pass

    def on_render(self):
        """
        Called during Widget.render call, this is where the the actual drawing to the Widget.surface should be done.

        This should be overridden by the subclassing Widget.  This default implementation will fill the surface
        with a random color.  Useful for debugging and seeing what is drawn to the screen..

        :return:
        """

        self.surface = pygame.Surface(self.layout.size)
        self.surface.fill(
            (
                random.randint(60, 255),
                random.randint(60, 255),
                random.randint(60, 255),
            )
        )

    def on_draw(self, surface, g_offset):
        """
        Blit the widget.surface to the passed surface.

        If Widget.use_surface = False, then do nothing.  In this case the subclass should override the
        Widget.on_draw method.

        :param surface: surface to blit the Widget.surface to.
        :param g_offset: additional offset to add to the rendering. This is only needed when the parent widget
                         does not use a surface, so it has to pass along its total_offset.
        :return: None
        """

        if self.use_surface:
            if self._dirty:
                self.render()

            pos = self.layout.total_offset
            pos += g_offset
            surface.blit(self.surface, pos)
