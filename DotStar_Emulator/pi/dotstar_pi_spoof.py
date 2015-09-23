import threading
from multiprocessing.connection import Client
try:
    import Queue as queue
except ImportError:
    import queue

__all__ = ["Adafruit_DotStar", ]

# // Method names are silly and inconsistent, but following NeoPixel
# // and prior libraries, which formed through centuries of accretion.

HOST = '127.0.0.1'
PORT = 6555


class DataThread(threading.Thread):
    def __init__(self):
        """
        Thread that manages multiproccessing Client to send data to the emulator app

        :return:
        """

        super(DataThread, self).__init__()
        self.host = HOST
        self.port = PORT

        self.running = True

        self.queue = queue.Queue()
        self.daemon = True

        self.connection = None

    def open_connection(self):
        """
        Open a connection to the specified port.

        :return: None
        """
        try:
            self.connection = Client((self.host, self.port))
        except:
            self.connection = None

    def run(self):
        while self.running:
            try:
                data = self.queue.get(timeout=0.01)
            except Queue.Empty:
                data = None

            if data:
                if not self.connection:
                    self.open_connection()

                if self.connection:
                    try:
                        self.connection.send(data)
                    except:
                        self.connection.close()
                        self.connection = None
                else:
                    # Don't let the queue buildup when a connection is not available. Just empty the
                    # queue
                    while not self.queue.empty():
                        self.queue.get(False)

    def stop(self):
        self.running = False


class Adafruit_DotStar(object):
    """
    // Allocate new DotStar object.  There's a few ways this can be called:
    // x = Adafruit_DotStar(nleds, datapin, clockpin)       Bitbang output
    // x = Adafruit_DotStar(nleds, bitrate)   Use hardware SPI @ bitrate
    // x = Adafruit_DotStar(nleds)            Hardware SPI @ default rate
    // x = Adafruit_DotStar()                 0 LEDs, HW SPI, default rate
    // 0 LEDs is valid, but one must then pass a properly-sized and -rendered
    // bytearray to the show() method.
    """

    # def __del__(self):
    #     print("Deleting")

    def __init__(self, *args):

        self._data_thread = DataThread()
        self._data_thread.start()

        self.numLEDs = None
        self.pixels = None
        self.brightness = 0

        # -------------------------------------
        # DotStar new
        args_count = len(args)

        # Argument count from dotstar.c DotStar_new object initialization

        # args_count == 3: Pixel count, data pin, clock pin
        # args_count == 2: Pixel count, hardware SPI bitrate
        # args_count == 1: Pixel count (hardware SPI w/default bitrate
        if args_count == 3 or args_count == 2 or args_count == 1:
            # disregard data_pin and clock pin, not needed in spoofer
            self.numLEDs = args[0]

        # args_count == 0: No LED bugger (raw writes only), default SPI bitrate
        elif args_count == 0:
            self.numLEDs = 0

        # args_count ERROR
        else:
            raise AttributeError("unexpected number of arguments")

        # Allocate buffer for pixels
        if self.numLEDs:
            self.pixels = bytearray(self.numLEDs * 4)

        # -------------------------------------
        # DotStar init
        for i in range(0, self.numLEDs * 4, 4):
            self.pixels[i] = 0xFF

    @staticmethod
    def begin():
        """
        // Initialize pins/SPI for output
        """

        # No need to do anything here, as we are not setting up and actual SPI information.

    def clear(self):
        """
        // Set strip data to 'off' (just clears buffer, does not write to strip)
        """
        for i in range(0, len(self.pixels), 4):
            self.pixels[i + 1] = 0x00
            self.pixels[i + 2] = 0x00
            self.pixels[i + 3] = 0x00

    def setBrightness(self, brightness):
        """
        // Set global strip brightness.  This does not have an immediate effect;
        // must be followed by a call to show().  Not a fan of this...for various
        // reasons I think it's better handled in one's application, but it's here
        // for parity with the Arduino NeoPixel library.
        """

        assert type(brightness) is int
        assert 0 <= brightness <= 255

        # // Stored brightness value is different than what's passed.  This
        # // optimizes the actual scaling math later, allowing a fast multiply
        # // and taking the MSB.  'brightness' is a uint8_t, adding 1 here may
        # // (intentionally) roll over...so 0 = max brightness (color values
        # // are interpreted literally; no scaling), 1 = min brightness (off),
        # // 255 = just below max brightness.
        self.brightness = brightness

    def setPixelColor(self, *args):
        """
        // Valid syntaxes:
        // x.setPixelColor(index, red, green, blue)
        // x.setPixelColor(index, 0x00RRGGBB)
        """

        args_count = len(args)

        # args_count == 4: Index, r, g, b
        if args_count == 4:
            i, r, g, b = args

        # args_count == 2: Index, value
        elif args_count == 2:
            i, v = args
            r = (v & 0x00FF0000) >> 16
            g = (v & 0x0000FF00) >> 8
            b = (v & 0x000000FF)

        # args_count ERROR
        else:
            raise AttributeError("unexpected number of arguments")

        if i < self.numLEDs:
            index = i * 4
            self.pixels[index + 1] = b
            self.pixels[index + 2] = g
            self.pixels[index + 3] = r

    def _raw_write(self, data):
        """
        // Private method.  Writes pixel data without brightness scaling.
        """
        out_buffer = bytearray()
        out_buffer += bytearray((0x00, 0x00, 0x00, 0x00))
        out_buffer += data

        if self.numLEDs:
            footerLen = (self.numLEDs + 15) / 16
        else:
            footerLen = ((len(data) / 4) + 15) / 16
        fBuf = bytearray()
        for i in range(footerLen):
            # This is different than AdaFruit library, which uses zero's in the xfer[2] spi_ioc_transfer struct.
            out_buffer.append(0xFF)

        self._data_thread.queue.put_nowait(out_buffer)
        # print(out_buffer)


    def X_raw_write(self, data):
        """
        // Private method.  Writes pixel data without brightness scaling.
        """

        self._data_thread.queue.put_nowait(bytearray((0x00, 0x00, 0x00, 0x00)))
        self._data_thread.queue.put_nowait(data)

        # self._data_thread.queue.put_nowait(bytearray((0xFF, 0xFF, 0xFF, 0xFF)))
        # if(self->numLEDs) xfer[2].len = (self->numLEDs + 15) / 16;
        # else              xfer[2].len = ((len / 4) + 15) / 16;

        if self.numLEDs:
            footerLen = (self.numLEDs + 15) / 16
        else:
            footerLen = ((len(data) / 4) + 15) / 16
        fBuf = bytearray()
        for i in range(footerLen):
            # This is different than AdaFruit library, which uses zero's in the xfer[2] spi_ioc_transfer struct.
            fBuf.append(0xFF)
        self._data_thread.queue.put_nowait(fBuf)
        # print(len(data), len(fBuf))

    def show(self, *args):
        """
        // Issue data to strip.  Optional arg = raw bytearray to issue to strip
        // (else object's pixel buffer is used).  If passing raw data, it must
        // be in strip-ready format (4 bytes/pixel, 0xFF/B/G/R) and no brightness
        // scaling is performed...it's all about speed (for POV, etc.)
        """
        if len(args) == 1:
            buf = args[0]
            self._raw_write(buf)
        else:
            scale = self.brightness

            if self.brightness == 0:  # // Send raw (no scaling)
                self._raw_write(bytearray(self.pixels))
            else:
                # // Scale from 'pixels' buffer into
                # // 'pBuf' (if available) and then
                # // use a single efficient write
                # // operation (thx Eric Bayer).
                pBuf = bytearray()
                for i in range(self.numLEDs):
                    index = i * 4
                    b = (self.pixels[index + 1] * scale) >> 8
                    g = (self.pixels[index + 2] * scale) >> 8
                    r = (self.pixels[index + 3] * scale) >> 8
                    pBuf.append(self.pixels[index])
                    pBuf.append(b)
                    pBuf.append(g)
                    pBuf.append(r)

                self._raw_write(pBuf)

    @staticmethod
    def Color(r, g, b):
        """
        // Given separate R, G, B, return a packed 32-bit color.
        // Meh, mostly here for parity w/Arduino library.
        """
        assert type(r) is int
        assert type(g) is int
        assert type(b) is int

        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

        return r << 16 | g << 8 | b

    def getPixelColor(self, i):
        """
        // Return color of previously-set pixel (as packed 32-bit value)
        """
        if i < self.numLEDs:
            index = i * 4
            b = index + 1
            g = index + 2
            r = index + 3
            return self.Color(r, g, b)

    def numPixels(self):
        """
        // Return strip length
        """
        return self.numLEDs

    def getBrightness(self):
        """
        // Return strip brightness
        """
        # TODO I am not sure what the AdaFruit DotStar method is doing
        # Can't find documenation for "H". Need to see behaviour on RaspberryPi to fix
        # PyObject *result = Py_BuildValue("H", (uint8_t)(self->brightness - 1));
        return self.brightness

    def close(self):
        pass
