from __future__ import print_function
from pygame.math import Vector2

from DotStar_Emulator.emulator import config

__all__ = ["MappingData", ]


class MappingData(object):

    def __init__(self):
        """
        Provide the mapping from a single series strip of DotStar pixels to an x, y grid

        :return:
        """

        self.grid_size = Vector2(config.get("GRID_SIZE"))
        self.pixel_count = 0

        self.data = [[None for x in range(int(self.grid_size.y))] for y in range(int(self.grid_size.x))]

        pixel_mapping = config.get("PIXEL_MAPPING")
        if pixel_mapping is not None:
            self.custom_mapping(pixel_mapping)
        else:
            self.prebuilt_mappings()
            self.pixel_count = int(self.grid_size.x * self.grid_size.y)

    def custom_mapping(self, pixel_mapping):

        columns, rows = self.confirm_customer_size(pixel_mapping)

        values = []
        for y in range(rows):
            for x in range(columns):
                index = pixel_mapping[y][x]
                if index is not None:
                    if index in values:
                        raise Exception("Custom PIXEL_MAPPING has duplicate pixel index value of '{}'".format(index))
                    else:
                        values.append(index)
                    self.data[x][y] = index

        values.sort()
        for i, index in enumerate(values):
            if i != index:
                print(i, index)
                raise Exception("Custom PIXEL_MAPPING values are not continuous, value '{}' is missing.".format(i))

        self.pixel_count = len(values)

    @staticmethod
    def confirm_customer_size(pixel_mapping):

        rows = len(pixel_mapping)
        if rows != int(Vector2(config.get("GRID_SIZE")).y):
            raise Exception("Custom PIXEL_MAPPING rows '{}' does not match GRID_SIZE.y '{}'".format(rows, int(
                Vector2(config.get("GRID_SIZE")).y)))

        columns = []
        for y in range(len(pixel_mapping)):
            x = len(pixel_mapping[y])
            if x not in columns:
                columns.append(x)

        if len(columns) != 1:
            raise Exception("Custom PIXEL_MAPPING columns malformed, all are not of equal length.")

        if columns[0] != int(Vector2(config.get("GRID_SIZE")).x):
            raise Exception("Custom PIXEL_MAPPING columns '{}' does not match GRID_SIZE.x '{}'".format(columns[0], int(
                Vector2(config.get("GRID_SIZE")).x)))

        return columns[0], rows

    def prebuilt_mappings(self):

        zero_location = config.get("ZERO_LOCATION")

        # Top Left
        if zero_location == 0:
            cardinal = False
            left_to_right = True

        # Top Right
        elif zero_location == 1:
            cardinal = False
            left_to_right = False

        # Bottom Left
        elif zero_location == 2:
            cardinal = True
            left_to_right = True

        # Bottom Right
        elif zero_location == 3:
            cardinal = True
            left_to_right = False

        # Configuration Error
        else:
            raise AttributeError("invalid ZERO_LOCATION configuration '{}'".format(zero_location))

        # Render the correct pattern
        pattern = config.get("PATTERN")
        if pattern == 0:
            self.vertical(cardinal, left_to_right)
        elif pattern == 1:
            self.vertical_daisy(cardinal, left_to_right)
        elif pattern == 2:
            self.horizontal(cardinal, left_to_right)
        elif pattern == 3:
            self.horizontal_daisy(cardinal, left_to_right)
        else:
            raise AttributeError("invlude PATTERN configuration '{}'".format(pattern))

    def get(self, x, y):
        """
        Return the pixel_index for a given grid x, y coordinate

        :param x: grid column, left = 0
        :param y: grid row, right = 0
        :return: pixel index
        """
        return self.data[x][y]

    def horizontal(self, cardinal=False, left_to_right=True):
        """
        Map pixel_index to the x, y grid

        cardinal = False        cardinal = False
        left_to_right = True    left_to_right=False
        00 01 02 03             03 02 01 00
        04 05 06 07             07 06 05 04
        08 09 10 11             11 10 09 08
        12 13 14 15             15 14 13 12

        cardinal = True         cardinal = True
        left_to_right = True    left_to_right=False
        12 13 14 15             15 14 13 12
        08 09 10 11             11 10 09 08
        04 05 06 07             07 06 05 04
        00 01 02 03             03 02 01 00

        :param cardinal:
        :param left_to_right:
        :return:
        """

        index = 0
        if not cardinal:
            r_y = range(int(self.grid_size.y))
        else:
            r_y = range(int(self.grid_size.y)-1, -1, -1)
        for y in r_y:
            if left_to_right:
                r_x = range(int(self.grid_size.x))
            else:
                r_x = range(int(self.grid_size.x)-1, -1, -1)
            for x in r_x:
                self.data[x][y] = index
                index += 1

    def vertical(self, cardinal=False, left_to_right=True):
        """
        Map pixel_index to the x, y grid

        cardinal = False        cardinal = False
        left_to_right = True    left_to_right=False
        00 04 08 12             12 08 04 00
        01 05 09 13             13 09 05 01
        02 06 10 14             14 10 06 02
        03 07 11 15             15 11 07 03

        cardinal = True         cardinal = True
        left_to_right = True    left_to_right=False
        03 07 11 15             15 11 07 03
        02 06 10 14             14 10 06 02
        01 05 09 13             13 09 05 01
        00 04 08 12             12 08 04 00

        :param cardinal:
        :param left_to_right:
        :return: None
        """

        index = 0
        if left_to_right:
            r_x = range(int(self.grid_size.x))
        else:
            r_x = range(int(self.grid_size.x)-1, -1, -1)
        for x in r_x:
            if not cardinal:
                r_y = range(int(self.grid_size.y))
            else:
                r_y = range(int(self.grid_size.y)-1, -1, -1)
            for y in r_y:
                self.data[x][y] = index
                index += 1

    def vertical_daisy(self, cardinal=False, left_to_right=True):
        """
        Map pixel_index to the x, y grid

        cardinal = False        cardinal = False
        left_to_right = True    left_to_right=False
        00 07 08 15             15 08 07 00
        01 06 09 14             14 09 06 01
        02 05 10 13             13 10 05 02
        03 04 11 12             12 11 04 03

        cardinal = True         cardinal = True
        left_to_right = True    left_to_right=False
        03 04 11 12             12 11 04 03
        02 05 10 13             13 10 05 02
        01 06 09 14             14 09 06 01
        00 07 08 15             15 08 07 00

        :param cardinal:
        :param left_to_right:
        :return: None
        """

        index = 0
        if left_to_right:
            r_x = range(int(self.grid_size.x))
        else:
            r_x = range(int(self.grid_size.x)-1, -1, -1)
        for x_i, x in enumerate(r_x):

            zig = False

            if cardinal:
                if x_i % 2 == 0:
                    zig = True
            else:
                if x_i % 2 == 1:
                    zig = True

            if zig:
                r_y = range(int(self.grid_size.y)-1, -1, -1)
            else:
                r_y = range(int(self.grid_size.y))

            for y in r_y:
                self.data[x][y] = index
                index += 1

    def horizontal_daisy(self, cardinal=False, left_to_right=True):
        """
        Map pixel_index to the x, y grid

        cardinal = False        cardinal = False
        left_to_right = True    left_to_right=False
        00 01 02 03             03 02 01 00
        07 06 05 04             04 05 06 07
        08 09 10 11             11 10 09 08
        15 14 13 12             12 13 14 15

        cardinal = True         cardinal = True
        left_to_right = True    left_to_right=False
        15 14 13 12             12 13 14 15
        08 09 10 11             11 10 09 08
        07 06 05 04             04 05 06 07
        00 01 02 03             03 02 01 00

        :param cardinal:
        :param left_to_right:
        :return: None
        """

        index = 0
        if not cardinal:
            r_y = range(int(self.grid_size.y))
        else:
            r_y = range(int(self.grid_size.y)-1, -1, -1)
        for y_i, y in enumerate(r_y):

            zig = False

            if left_to_right:
                if y_i % 2 == 1:
                    zig = True
            else:
                if y_i % 2 == 0:
                    zig = True

            if zig:
                r_x = range(int(self.grid_size.x)-1, -1, -1)
            else:
                r_x = range(int(self.grid_size.x))

            for x in r_x:
                self.data[x][y] = index
                index += 1
