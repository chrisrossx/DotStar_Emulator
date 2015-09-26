import os
import shutil
import sys
import argparse

from DotStar_Emulator.emulator import EmulatorApp
from DotStar_Emulator.emulator.send_test_data import start_send_test_data_app


# Main Parser
parser = argparse.ArgumentParser(prog="DotStar Emulator, A DotStar Strip Hardware Emulator")
sub_parser = parser.add_subparsers()

# Build Run Arguments
run_command = sub_parser.add_parser("run", help="run the emulator")
run_command.set_defaults(cmd="run")

# Build Test Arguments
test_data_command = sub_parser.add_parser("test", help="send test data")
test_data_command.set_defaults(cmd="test")
test_data_command.add_argument("--loop", dest="loop", action="store", default=None,
                               help="Repeat sending the data for the given number of times")

test_data_command.add_argument("--rate", dest="rate", action="store", default=None,
                               help="Repeat sending the data at the given frequency in Hz")

group = test_data_command.add_mutually_exclusive_group()
group.add_argument("--rand", dest="rand", action="store_const", const=True,
                   help="Color each cell randomly")
group.add_argument("--rblend", dest="rblend", action="store_const", const=True,
                   help="[DEFAULT] (b, g, r) Color each cell randomly")
group.add_argument("--fill", dest="fill", action="store", metavar="color",
                   help="Flood Fill with 'color' (b, g, r)")
group.add_argument("--image", dest="image", action="store", metavar="filename",
                   help="Load image")

# Build Init Arguments
init_command = sub_parser.add_parser("init", help="Initialise the working folder with a config and manage.py file.")
init_command.set_defaults(cmd="init")
init_command.add_argument("--force", dest="force", action="store_const", const=True, default=False,
                          help="Overwrite existing files.")


def run(arguments):
    """
    Run the main emulator application.

    :param arguments: argparse Namespace
    :return: None
    """

    app = EmulatorApp()
    app.run()


def send_test_data(arguments):
    """
    use TCP socket to send test data to a running instance of DotStar Emulator

    :param arguments: argparse Namespace
    :return: None
    """

    start_send_test_data_app(arguments)


def init(arguments):
    """
    Initialize a users folder with a config and manage.py file.

    :param arguments: argparse Namespace
    :return: None
    """

    print("Initializing folder with DotStar_Emulator files")

    source_folder = os.path.realpath(os.path.join(os.path.dirname(__file__), 'emulator', 'init'))
    dest_folder = os.getcwd()
    for filename in os.listdir(source_folder):
        if not '.pyc' in os.path.splitext(filename):
            source_file = os.path.join(source_folder, filename)
            dest_file = os.path.join(dest_folder, filename)
            if arguments.force is False and os.path.isfile(dest_file):
                print("Error, file already exists in current folder filename: '{}' use --force to overwrite files.".format(
                    filename))
            else:
                shutil.copy(source_file, dest_file)
                print("Copying filename: '{}'".format(filename))


def manage():
    """
    Main entry point into the application.

    :return: None
    """

    # No Arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(sys.argv[1:])

    if 'cmd' in args:
        if args.cmd == "run":
            run(args)
        if args.cmd == "test":
            send_test_data(args)
        if args.cmd == "init":
            init(args)
    else:
        if 'show_help' in args:
            args.show_help.print_help()

if __name__ == "__main__":
    manage()
