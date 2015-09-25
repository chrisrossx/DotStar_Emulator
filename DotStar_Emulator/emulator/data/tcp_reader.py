from __future__ import print_function
import threading
import logging
from multiprocessing.connection import Listener
import select

from DotStar_Emulator.emulator import config, globals

log = logging.getLogger("data")

__all__ = ["TCPReader", ]


class TCPReader(threading.Thread):
    def __init__(self):
        """
        Read emulator strip SPI data in a TCP socket.
        TCPReader runs in its own thread, and will acquire a lock from strip_data before
        writing data.

        HOST and PORT set in config.

        :return:
        """
        super(TCPReader, self).__init__()

        self.host = config.get("HOST")
        self.port = config.get("PORT")
        self.listener = None

        # Thread Loop
        self.running = True

        # Report back to the main thread if we could bind to the port or not. Main thread will not continue
        # if port was not bound to.
        self.startup = threading.Event()
        self.startup_success = False

    def open_listener(self):
        """
        Open Listener to the specified socket.  Set an event and report to the main thread if it was successful

        :return: None
        """

        try:
            self.listener = Listener((self.host, self.port))
            self.startup_success = True
            log.info("listening on '%s', %s", self.host, self.port)
        except:
            self.startup_success = False
            log.exception("Could not bind socket '%s', %s", self.host, self.port)

        self.startup.set()
        return self.startup_success

    def run(self):
        """
        Run the TCPReader thread to open and listen on a TCP socket for a connection to emulate the SPI bus.

        :return: None
        """
        log.info("Starting thread")
        if self.open_listener():

            # This feels so dirty, but we need to make sure the thread isn't always blocking so we
            # can safely shutdown the thread.  Given that the Listener address is always an IP
            # it should be safe. Should be, famous last words of course...
            conn = self.listener._listener._socket

            while self.running:
                r_list, w_list, e_list = select.select([conn, ], [conn, ], [conn, ], 0.01)

                if conn in r_list:
                    connection = None
                    try:
                        connection = self.listener.accept()
                        log.info("Connection opened by %s", self.listener.last_accepted)

                        while self.running:
                            if connection.poll():
                                msg = connection.recv()
                                globals.strip_data.spi_recv(msg)
                    except (IOError, EOFError):
                        if connection:
                            connection.close()
                        log.info("Connection closed %s", self.listener.last_accepted)

        log.info("Exiting thread")

    def stop(self):
        log.info("Stopping thread")
        self.running = False
