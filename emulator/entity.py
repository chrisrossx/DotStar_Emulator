

class Entity(object):
    def __init__(self):
        """
        Base class for Entity objects. Entity objects provide an API for them to be updated and drawn from a Scene
        object.

        :return:
        """

    def on_draw(self, surface):
        """
        Called every game loop. Draw or blit to the surface to draw the entity to the screen.

        Called before the gui has been drawn. any draw/blit calls will be covered by the the gui if they overlap.

        :param surface: surface to blit the Widget.surface to.
        :return: None
        """

    def on_draw_after(self, surface):
        """
        Called every game loop. Draw or blit to the surface to draw the entity to the screen.

        Called after the gui has been drawn, any draw / blit calls will be drawn on top of the gui.

        :param surface: surface to blit the Widget.surface to.
        :return: None
        """

    def update(self, elapsed):
        """
        Called every game loop iteration independently of any draw or render requests.

        :param elapsed: milliseconds og pygame clock since last call
        :return:
        """
