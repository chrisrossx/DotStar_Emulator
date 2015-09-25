from __future__ import print_function

import blinker
import pygame

from DotStar_Emulator.emulator.entity import Entity
from DotStar_Emulator.emulator import config
from DotStar_Emulator.emulator.vector2 import Vector2

class DotGridSelect(Entity):
    def __init__(self, dotgrid):
        super(DotGridSelect, self).__init__()

        self.dotgrid = dotgrid

        self.clear_event = blinker.signal("dotgrid.select.clear")
        self.set_event = blinker.signal("dotgrid.select.set")

        self.step = 0
        self.elapsed = 0
        self.speed = config.get("DOT_GRID_SELECT_SPEED")
        self.colors = config.get("DOT_GRID_SELECT_COLORS")

        self.x = 0
        self.y = 0
        self.rect = None
        self.selected = False

        blinker.signal("event.mousebuttondown").connect(self.on_mousebuttondown)
        blinker.signal("event.keydown").connect(self.on_keydown)

    def set(self, x, y):
        """
        Set the highlighter to the given grid cell.
        Trigger Blinker Event "dotgrid.select.set"
        :param x: Integer
        :param y: Integer
        :return: None
        """

        if self.selected:
            self.clear()
        self.x = x
        self.y = y

        self.selected = True
        self.set_event.send(self, x=self.x, y=self.y)

    def clear(self):
        """
        Clear the highlighter to the given grid cell.
        Trigger Blinker Event "dotgrid.select.clear" if there was a highlighted cell

        :return: True or False
        """
        if self.selected:
            self.clear_event.send(self, x=self.x, y=self.y)
            self.selected = False
            return True
        return False

    def on_mousebuttondown(self, sender, event):

        global_rect = self.dotgrid.layout.global_rect

        if global_rect.collidepoint(event.pos):
            grid_size = self.dotgrid.grid_size
            grid_rects = self.dotgrid.grid_rects
            pos = Vector2(event.pos) - Vector2(global_rect.topleft)
            for x in range(int(grid_size.x)):
                for y in range(int(grid_size.y)):
                    if grid_rects[x][y].collidepoint(pos):
                        if self.selected and self.x == x and self.y == y:
                            self.clear()
                        else:
                            # self.clear()
                            self.set(x, y)

    def on_keydown(self, sender, event):
        """
        pygame event KEYDOWN event call back.  Allow cursor keys to operate the select position.
        Escape key will clear current selection.

        :param sender:
        :param event: pygame Event
        :return: None
        """

        if not self.selected:
            if event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]:
                self.set(self.x, self.y)
        else:
            if event.key == pygame.K_ESCAPE:
                self.clear()
            if event.key == pygame.K_DOWN:
                y = self.y + 1 if self.y < self.dotgrid.grid_size.y - 1 else 0
                x = self.x
                self.set(x, y)
            if event.key == pygame.K_UP:
                y = self.y - 1 if self.y > 0 else int(self.dotgrid.grid_size.y) - 1
                x = self.x
                self.set(x, y)
            if event.key == pygame.K_RIGHT:
                x = self.x + 1 if self.x < self.dotgrid.grid_size.x - 1 else 0
                y = self.y
                self.set(x, y)
            if event.key == pygame.K_LEFT:
                x = self.x - 1 if self.x > 0 else int(self.dotgrid.grid_size.x) - 1
                y = self.y
                self.set(x, y)

    def update(self, elapsed):
        self.elapsed += elapsed
        if self.elapsed >= self.speed:
            self.elapsed = 0
            self.step += 1
            if self.step >= 4:
                self.step = 0

    def on_draw_after(self, surface):
        # print('on_draw_after', self.dotgrid)
        if self.selected:
            grid_rect = self.dotgrid.grid_rects[self.x][self.y]
            rect = grid_rect.copy()
            rect.x += self.dotgrid.layout.global_rect.x
            rect.y += self.dotgrid.layout.global_rect.y

            size = [0, 2, 4, 2][self.step]
            rect.inflate_ip(size, size)

            pygame.draw.rect(surface, self.colors[0], rect, 1)
            rect.inflate_ip(2, 2)
            pygame.draw.rect(surface, self.colors[1], rect, 1)
