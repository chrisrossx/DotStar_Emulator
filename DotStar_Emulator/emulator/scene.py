from pygame.math import Vector2
from . import globals

from .gui import FILLX, FILLY


class Scene(object):

    def __init__(self):
        """
        Base class for Scene objects. Scenes control a specific Screen / part of the app.  Similar to a game
        level or menu or other object.  One scene is displayed and updated from the main loop at a time.

        :return:
        """
        self.panel = None
        self._entities = []

    def add_entity(self, entity):
        """
        Entities are non gui/widget objects that will be rendered and updated.

        :param entity: subclass Entity
        :return: None
        """
        self._entities.append(entity)

    def update(self, elapsed):
        """
        Update the gui and all entities.

        :param elapsed: milliseconds og pygame clock since last call
        :return: None
        """
        for entity in self._entities:
            entity.update(elapsed)

        self.panel.update(elapsed)

    def on_draw(self, surface):
        """
        Root on_draw method called directly from the game loop.

        :param surface: pygame.Surface
        :return: None
        """

        # Provide a draw hook before the gui is drawn
        for entity in self._entities:
            entity.on_draw(surface)

        # Draw the root gui panel/widget
        self.panel.on_draw(surface, Vector2(0, 0))

        # Provide a draw hook after the gui is drawn
        for entity in self._entities:
            entity.on_draw_after(surface)

    def set_panel(self, panel):
        """
        Set the main gui panel for the scene.

        :param panel: root gui.panels.Widget
        :return: None
        """
        self.panel = panel

    def fit(self):
        """
        Root fit method, will automatically start the sizing of the hierarchy of gui widgets.

        :return: None
        """

        # The root widget, should fill the screen surface
        size = Vector2(globals.current_app.window_size)
        self.panel.fit(size, Vector2(0, 0), Vector2(0, 0), FILLX | FILLY)
