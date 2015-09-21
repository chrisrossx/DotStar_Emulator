"""
Configuration is global
"""

import os
import imp


_DEFAULT = {
    ######################################################################################
    #
    # pygame Configurations
    #
    "WINDOW_SIZE": (640, 480),
    # "WINDOW_SIZE": (800, 600),
    # "FULL_SCREEN": False,

    ######################################################################################
    #
    # Grid size of pixel placement drawing board
    #
    # "GRID_SIZE": (16, 24),  # columns, rows
    # "GRID_SIZE": (4, 4),  # columns, rows
    "GRID_SIZE": (8, 8),  # columns, rows
    # "GRID_SIZE": (64, 64),  # columns, rows
    # "GRID_SIZE": (32, 32),  # columns, rows
    # "GRID_SIZE": (3, 2),  # columns, rows
    "BORDER_SIZE": (1, 1),  # px
    "PERIMETER_BORDER_SIZE": (3, 3),  # px, draw a perimeter border around the grid of pixels px
    "SQUARE_LED": True,  # square up the led when calculating its size. otherwise LED shape will fill the screen space

    "PIXEL_MAPPING": None,

    ######################################################################################
    #
    # Grid pixel order
    #

    # Set Zero Location
    #   Top Left = 0
    #   Top Right = 1
    #   Bottom Left = 2
    #   Bottom Right = 3
    "ZERO_LOCATION": 0,

    # Set Pattern
    #   vertical = 0
    #   vertical zigzag = 1
    #   horizontal = 2
    #   horizontal zigzag = 3
    #
    # Below are visual example patterns with the Zero location in the top left.
    #
    #   0.Vertical      1.Vertical Zig      2.Horizontal    3. Horizontal Zig
    #   00 04 08 12     00 07 08 15         00 01 02 03     00 01 02 03
    #   01 05 09 13     01 06 09 14         04 05 06 07     07 06 05 04
    #   02 06 10 14     02 05 10 13         08 09 10 11     08 09 10 11
    #   03 07 11 15     03 04 11 12         12 13 14 15     15 14 13 12
    "PATTERN": 0,

    ######################################################################################
    #
    # Socket Settings
    #
    "HOST": '127.0.0.1',
    "PORT": 6555,

    ######################################################################################
    #
    # Logging Configurations
    #
    "LOGGING": {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)-8s - %(levelname)-6s - %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'DEBUG',
                'propagate': True,
            },
            # 'app': {
            #     'level': 'INFO',
            # },
            # 'debug': {
            #     'level': 'INFO',
            # },
        }
    },

}

_READ_ONLY = {
    "WINDOW_CAPTION": "DotStar Emulator",
    "EMU_RUNNING_MIN_RIGHT_COL_WIDTH": -300,
    "FPS_UPDATE_RATE": 50,

    "DOT_GRID_SELECT_SPEED": 150,
    "DOT_GRID_SELECT_COLORS": (
        (255, 0, 255, 255),
        (255, 0, 0, 255),
    ),

    "DRAW_INDEXES": 0,
    "DRAW_INDEXES_COLORS": (
        (255, 0, 255),
        (255, 255, 255),
        (20, 20, 20)
                            ),
    "DRAW_BORDERS": 1,
    "DRAW_BORDERS_COLORS": (
        (40, 40, 40),
        (255, 255, 255),
        (255, 0, 255),
        (0, 0, 0),
                            ),

    "BRAND_TITLE": (33, 150, 214, 255),
    "BRAND_HR": (30, 30, 30, 255),
    "BRAND_TEXT_HEADER": (255, 240, 87, 255),
    "BRAND_BOX_BG": (40, 40, 40, 255),



}

_LOADED_VALUES = {

}


def get(key):
    """
    Return a configuration setting, will first look for loaded values then return a default if
    it exists.

    :param key: key for configuration value
    :return: configuration value
    """

    if key in _READ_ONLY:
        return _READ_ONLY.get(key)

    if key in _DEFAULT:
        return _LOADED_VALUES.get(key, _DEFAULT[key])
    else:
        return _LOADED_VALUES.get(key)


def set(key, value):
    """
    Sets a configuration setting.

    :param key: key for configuration value
    :param value: configuration value
    :return:
    """

    _LOADED_VALUES[key] = value


def read_configuration():
    filename = os.path.join(os.getcwd(), 'config.py')
    if os.path.isfile(filename):

        d = imp.new_module('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise

        for key, value in d.__dict__.items():
            if key.isupper():
                set(key, value)
        return True
    return False
