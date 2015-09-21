from __future__ import print_function
import socket
import random
import os
import time
from PIL import Image

import pygame
from pygame.math import Vector2

from DotStar_Emulator.emulator import config
from DotStar_Emulator.emulator.utils import blend_color
from DotStar_Emulator.emulator.data import MappingData


class App(object):

    data_type = None

    def __init__(self, args):
        self.args = args
        self.mapping_data = MappingData()

        self.grid_size = Vector2(config.get("GRID_SIZE"))
        self.pixel_count = self.mapping_data.pixel_count
        size = self.pixel_count * 4

        # data does not include start and end bytes
        self.data = bytearray(size)
        self.socket = None

        print("Data Type:", self.data_type)

        if self.args.rate:
            self.repeat_mode = "rate"
            self.repeat_rate = float(self.args.rate)
            print("Repeat Mode: Frequency")
            print('Frequency Set:', self.repeat_rate)

        else:
            self.repeat_mode = "loop"
            if self.args.loop:
                self.range = range(int(args.loop))
                print("Repeat Mode: Loop")
                print("Loops Count:", args.loop)
            else:
                print("Repeat Mode: None, send once")
                self.range = range(1)

    def set(self, index, c, b, g, r):
        if index is not None and index < self.pixel_count:
            i = index * 4
            self.data[i] = c
            self.data[i+1] = b
            self.data[i+2] = g
            self.data[i+3] = r

    def run(self):
        if self.repeat_mode == "loop":
            try:
                for i in self.range:
                    self.on_loop()
            except KeyboardInterrupt:
                pass
        elif self.repeat_mode == "rate":
            rate = 1.0 / self.repeat_rate
            try:
                while True:
                    time.sleep(rate)
                    self.on_loop()
            except KeyboardInterrupt:
                pass

    def send(self):

        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            self.socket.connect((config.get("HOST"), config.get("PORT")))

        # Start
        self.socket.send(bytearray((0x00, 0x00, 0x00, 0x00)))

        self.socket.send(self.data)

        # End Frame
        self.socket.send(bytearray((0xFF, 0xFF, 0xFF, 0xFF)))

    def on_loop(self):
        raise NotImplementedError

    @staticmethod
    def rand_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return pygame.Color(r, g, b)


class RandomBlendApp(App):

    data_type = "Random blend"

    def fill_dummy(self):
        a = self.rand_color()
        r = self.rand_color()
        g = self.rand_color()
        b = self.rand_color()

        for x in range(int(self.grid_size.x)):
            for y in range(int(self.grid_size.y)):

                c1 = blend_color(a, r, (x / self.grid_size.x))
                c2 = blend_color(g, b, (x / self.grid_size.x))
                c = blend_color(c1, c2, (y / self.grid_size.y))
                i = self.mapping_data.get(x, y)

                self.set(i, 0xFF, c.b, c.g, c.r)

    def on_loop(self):
        self.fill_dummy()
        self.send()


class RandomColorApp(App):

    data_type = "Random colors"

    def fill_dummy(self):

        for x in range(int(self.grid_size.x)):
            for y in range(int(self.grid_size.y)):
                i = self.mapping_data.get(x, y)
                c = self.rand_color()
                self.set(i, 0xFF, c.b, c.g, c.r)

    def on_loop(self):
        self.fill_dummy()
        self.send()


class FillApp(App):

    data_type = "Fill single color"

    def fill(self, b, r, g):
        for index in range(self.mapping_data.pixel_count):
            print(index)
            self.set(index, 0xFF, b, g, r)

        # for x in range(int(self.grid_size.x)):
        #     for y in range(int(self.grid_size.y)):
        #         i = self.mapping_data.get(x, y)

    def on_loop(self):
        fill = self.args.fill
        if fill.startswith("(") and fill.endswith(")"):
            try:
                fill = fill[1:-1]
                parts = fill.split(",")
                # if len(parts) == 3:
                b = int(parts[0])
                g = int(parts[1])
                r = int(parts[2])
            except:
                raise AttributeError("Could not parse color")
        else:
            try:
                color = pygame.Color(fill)
                b = color.b
                r = color.r
                g = color.g
            except:
                raise AttributeError("Could not parse color")

        self.fill(b, r, g)
        self.send()


class ImageApp(App):

    data_type = "Image"

    def on_loop(self):

        filename = self.args.image
        if not os.path.isfile(filename):
            raise AttributeError("image file not found")

        im = Image.open(filename)
        rgb_im = im.convert('RGB')
        width = self.grid_size.x if im.size[0] >= self.grid_size.x else im.size[0]
        height = self.grid_size.y if im.size[1] >= self.grid_size.y else im.size[1]
        for x in range(int(width)):
            for y in range(int(height)):
                r, g, b = rgb_im.getpixel((x, y))
                i = self.mapping_data.get(x, y)
                self.set(i, 0xFF, b, g, r)

        self.send()


def start_send_test_data_app(args):

    config.read_configuration()

    if 'fill' in args and args.fill is not None:
        FillApp(args).run()
    elif 'image' in args and args.image is not None:
        ImageApp(args).run()
    elif 'rand' in args and args.rand is not None:
        RandomColorApp(args).run()
    else:
        RandomBlendApp(args).run()
