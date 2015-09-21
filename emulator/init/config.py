######################################################################################
#
# pygame Configurations
#

# pygame main window size
# WINDOW_SIZE = (640, 480)

# display in full screen mode
# FULL_SCREEN = True


######################################################################################
#
# Grid size of pixel placement drawing board
#

# Number of Rows and Columns of LEDS
# GRID_SIZE = (8, 8)

# Change border size of each LED. Default is 1, 1.  Unit is pixels
# BORDER_SIZE = (1, 1)

# Change the border size around the whole array of LED's.  Unit is pixels
# PERIMETER_BORDER_SIZE = (3, 3)  # px, draw a perimeter border around the grid of pixels px


# Take up whole screen space by having LED's stretch to fill the space.
# SQUARE_LED = False


######################################################################################
#
# Automatic Grid pixel order
#

# Set Zero Location
#   Top Left, 0
#   Top Right, 1
#   Bottom Left, 2
#   Bottom Right, 3
# ZERO_LOCATION = 0

# Set Pattern
#   vertical, 0
#   vertical zigzag, 1
#   horizontal, 2
#   horizontal zigzag, 3
#
# Below are visual example patterns with the Zero location in the top left.
#
#   0.Vertical      1.Vertical Zig      2.Horizontal    3. Horizontal Zig
#   00 04 08 12     00 07 08 15         00 01 02 03     00 01 02 03
#   01 05 09 13     01 06 09 14         04 05 06 07     07 06 05 04
#   02 06 10 14     02 05 10 13         08 09 10 11     08 09 10 11
#   03 07 11 15     03 04 11 12         12 13 14 15     15 14 13 12

# PATTERN = 1

######################################################################################
#
# Custom Grid Pixel Mapping
#

# It is possible to override any automatic grid pixel index mapping by deffining
# a PIXEL_MAPPING[x][y] list of indexes.  It is not required to fill the entire grid
# with pixel indexes.  However,
#   * Indexes must start at zero.
#   * Can not skip any indexes.
#   * Do not have to be in any kind of order on the grid.
#   * use None, to define an empty grid location.

# This below example only defines 12 out of 16 possible grid locations.

# PIXEL_MAPPING = [
#     [None, 0, 1, None],
#     [6, 7, 8, 9],
#     [2, 3, 4, 5],
#     [None, 10, 11, None],
# ]

######################################################################################
#
# Socket Settings
#

# Allow connections from any machine.  otherwise only allow from localhost
# HOST = '0.0.0.0'

# Change port number of TCP connection
# PORT = 6555

######################################################################################
#
# Logging Configurations
#

# Its possible to change the default logging display

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'standard': {
#             'format': '%(asctime)s - %(name)-8s - %(levelname)-6s - %(message)s'
#         },
#     },
#     'handlers': {
#         'default': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard'
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['default'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'app': {
#         #     'level': 'INFO',
#         },
#         'data': {
#         #     'level': 'INFO',
#         },
#     }
# }
