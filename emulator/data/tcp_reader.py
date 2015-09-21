from __future__ import print_function
import threading
import time
import socket
import logging
import select


from DotStar_Emulator.emulator import config, strip_data

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
        self.backlog = 5
        self.size = 1024
        self.server = None

        # Thread Loop
        self.running = True

        # Report back to the main thread if we could bind to the port or not. Main thread will not continue
        # if port was not bound to.
        self.startup = threading.Event()
        self.startup_success = False

    def open_socket(self):
        """
        Bind to the specified socket.  Set an event and report to the main thread if it was successful

        :return: None
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setblocking(0)
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)

            # Set events and return
            log.info("listening on '%s', %s", self.host, self.port)
            self.startup_success = True
            self.startup.set()
            return True
        except socket.error:
            if self.server:
                self.server.close()

            # Set events and return
            log.exception("Could not bind socket '%s', %s", self.host, self.port)
            self.startup_success = False
            self.startup.set()
            return False

    def run(self):
        """
        Run the TCPReader thread to open and listen on a TCP socket for a connection to emulate the SPI bus.

        :return: None
        """
        log.info("Starting thread")
        if self.open_socket():

            while self.running:

                try:
                    conn, addr = self.server.accept()
                except socket.error:
                    conn, addr = None, None

                if conn:
                    log.info("Connection opened by '%s'", addr[0])
                    buff = bytearray()
                    while self.running:
                        rlist, wlist, elist = select.select([conn, ], [conn, ], [conn, ], 0.1)
                        if conn in rlist:
                            try:
                                data = conn.recv(1)
                            except:
                                data = None

                            if not data:
                                break

                            for i in data:
                                strip_data.spi_in(ord(i))

                        elif conn in elist:
                            break

                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    log.info("Connection closed '%s'", addr[0])

                # while waiting for a connection, don't burn through the CPU
                time.sleep(0.01)

            self.server.close()
        log.info("Exiting thread")

    def stop(self):
        log.info("Stopping thread")
        self.running = False
