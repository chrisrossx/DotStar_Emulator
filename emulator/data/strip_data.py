import logging
import datetime

from pygame.math import Vector2
import blinker

from DotStar_Emulator.emulator import config, mapping_data


app_log = logging.getLogger("app")
data_log = logging.getLogger("data")

__all__ = ["StripData", ]


class StripData(object):

    def __init__(self):
        """
        Data model of a strip of LED's and also handles processes received data packets.

        :return:
        """
        self.grid_size = Vector2(config.get("GRID_SIZE"))

        # self.pixel_count = int(self.grid_size.x * self.grid_size.y)
        self.pixel_count = mapping_data.pixel_count

        # setup initial pixel data
        size = self.pixel_count * 4
        self.data = bytearray(size)
        self.clear_data()

        self.spi_index = 0  # current pixel index of the spi_in function

        self.updated = None  # datetime of last time start frame was received
        self.packet_length = 0  # count of number of individual bytes received since last start frame was received.

        self._dirty = True  # keep track if data has been changed since last update call

        # cache blinker signals
        self._signal_startrecv = blinker.signal("stripdata.startrecv")
        self._signal_updated = blinker.signal("stripdata.updated")

        self.header_bytes_found = 0
        self.buffer_count = 0
        self.buffer = bytearray((0xFF, 0xFF, 0xFF, 0xFF))

    def spi_recv(self, msg):
        """
        Currently no checking of msg integrity or first four bytes being 0x00 is done. Msg is assumed
        to be correct. Future versions may provide a config that can be set that will perform
        some checks on the message, and search for the first data byte.

        :param msg: bytearray
        :return: None
        """

        msg_length = len(msg)
        data_length = len(self.data)

        # Check if message is longer than pixel count
        if (msg_length - 4) / 4 >= data_length:
            end = data_length
        else:
            end = (msg_length - 4)

        # Splice in the data from the message
        self.data[0:end] = msg[4:end+4]

        self._signal_startrecv.send(self)
        self.updated = datetime.datetime.now()
        self.packet_length = msg_length
        self._dirty = True

    def update(self, elapsed):
        """
        Because we don't really know when we have received the end of the data stream, we can't easily single the
        display to update, so instead we will look on every frame when update is called, and send the signal if
        any data has changed.

        :param elapsed: milliseconds
        :return: None
        """

        if self._dirty:
            self._signal_updated.send(self)
            self._dirty = False

    def clear_data(self):
        """
        Clear the pixel data data

        :return: None
        """
        for i in range(self.pixel_count):
            r = 0x00
            g = 0x00
            b = 0x00
            self.set(i, 0xFF, b, g, r)

    def set(self, index, c, b, g, r):
        """
        Set the pixel data for the given pixel index.  Because the data steam should always be longer than the
        number of pixels (end frame data), we will check if the index is within bounds of the display. If it is not
        without bounds, just ignore.

        :param index: `int` pixel index
        :param c: `byte` Control byte value
        :param b: `byte` Blue color value
        :param g: `byte` Green color value
        :param r: `byte` Red color Value
        :return: None
        """
        if index < self.pixel_count:
            i = index * 4
            self.data[i] = c
            self.data[i+1] = b
            self.data[i+2] = g
            self.data[i+3] = r
            self._dirty = True

    def get(self, index):
        """
        Return the stored pixel data for the given index

        :param index: `integer` of the pixel index
        :return: (c, b, g, r)
        """
        i = index * 4
        c = self.data[i]
        b = self.data[i+1]
        g = self.data[i+2]
        r = self.data[i+3]
        return c, b, g, r
