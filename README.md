# Introduction

A simple emulator/simulator for the AdaFruit DotStar Strip Library. This project allows for quicker development of DotStar controller programs that you write, by not requiring you to have hardware hooked up to your device. For example, you can program a Raspberry pi controller from your normal PC using this.

It works in two parts, the emulator application that runs and displays a virtual DotStar Strip, and a spoofed library that you load instead of the AdaFruit Libraries.  This allows you to display a virtual Strip on your screen instead of hooking up the hardware during some portion of your development cycle.

### Screenshots

[<img src="screenshot_001.jpg" alt="Running on Windows" width=250 height=250 />](screenshot_001.jpg)   [<img src="screenshot_002.jpg" alt="Running on Windows" width=250 height=250 />](screenshot_002.jpg)

# Installation

1.  Download from github
2.  `pip install -r requirements.txt`

# Getting Started

### DotStar Emulator consists of two parts.
 
1.  **Emulator application**.  This is a pygame application that will display a representation of your DotStar strip. Seen in the screenshot above. 
2.  **Spoofed AdaFruit DotStar_Pi Library** or **Spoofed AdaFruit Arduino DotStar Library**.  The purpose of these spoofed libraries is to be a drop in replacement for the AdaFruit Libraries. But instead of sending SPI data to the DotStar Strip in hardware, it will send the data to the DotStar Emulator application.

### Running the emulator application

Quickly start the emulator application with the default configuration, an (8, 8) grid of pixels.
 
    python -M DotStar_Emulator run

However this is only so useful, as you will most likely need to configure the emulator for your setup.  The preferred way to do this is to create a working directory where the DotStar_Emulator application can copy some files for you.

From the directory you want to copy the project files to:
    
    python -M DotStar_Emulator init

This will copy two files to the current working directory.
1.  **manage.py**, helper utility to quickly start the application and perform some other tasks. 
2.  **config.py**, edit this file to customize your configuration. 

Now you can start the Emulator application using:

    python manage.py run

### Spoofing the AdaFruit Libraries

##### AdaFruit_DotStar_Pi, Raspberry Pi Library

##### AdaFruit_DotStar, Adruino Library

Future Release

# Emulator Application Configuration

In the above step a config.py was created in your project working directory.  This file is commented with some helpful information for configuring your project.  the config.py file will automatically be loaded if its in your current working directory. 

# Additional Resources

* [Github Adafruit_DotStar_Pi](https://github.com/adafruit/Adafruit_DotStar_Pi)
* [Github Adafruit_DotStar](https://github.com/adafruit/Adafruit_DotStar)
* [Understanding the APA102 "Superled"](https://cpldcpu.wordpress.com/2014/11/30/understanding-the-apa102-superled/)

# Open Source Credits

1.  [Inconsolata-LGC Font](https://github.com/DeLaGuardo/Inconsolata-LGC), SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007

# License

[MIT LICENSE](http://opensource.org/licenses/MIT)
