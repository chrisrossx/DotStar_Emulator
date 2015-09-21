import threading
import time

import blinker


class RateCounter(threading.Thread):

    def __init__(self):
        """
        Thread to count frequency of incoming SPI packets.

        :return: None
        """

        super(RateCounter, self).__init__()

        # Thread Loop
        self.running = True

        self.count = 0
        blinker.signal("stripdata.startrecv").connect(self.on_stripdata_updated)
        self.rate_signal = blinker.signal("ratecounter.updated")

    def on_stripdata_updated(self, sender):
        """
        callback blinker signal of strap_data start frame received.

        :param sender: blinker sender
        :return: None
        """

        self.count += 1

    def run(self):
        """
        Thread sends signal to display frequency every 1 second.

        :return: None
        """

        elapsed = 0
        while self.running:
            time.sleep(0.05)
            elapsed += 0.05
            if elapsed >= 1:
                self.rate_signal.send(self, count=self.count)
                self.count = 0
                elapsed = 0

    def stop(self):
        """
        Signal the thread loop to stop.

        :return: None
        """

        self.running = False
