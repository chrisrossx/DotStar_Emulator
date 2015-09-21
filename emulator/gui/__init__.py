"""
Collection of helper classes to layout the gui using Widgets and Panels.
A widget is a any gui entity.  A panel is a widget which can have children widgets.

The gui automatically does layout in a fashion sillier to wxPython.
A Widget is a gui entity that displays something. IE; button, text label.
A panel is a gui widget which can hold other widgets.
"""

from .flags import *
from .widget import *
from .text import *
from .button import *
from .panels import *
