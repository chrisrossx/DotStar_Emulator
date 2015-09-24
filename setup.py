from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

long_description = """A simple emulator/simulator for the AdaFruit DotStar Strip Library.
This project allows for quicker development of DotStar controller
programs that you right, by not requiring you to have hardware
hooked up to your device. For example, you can program a Raspberry
pi controller from your normal PC using this.

License: MIT
Website: https://github.com/chrisrossx/DotStar_Emulator"""

setup(
    name="DotStar_Emulator",
    version='0.0.dev2',
    url='https://github.com/chrisrossx/DotStar_Emulator',
    description='DotStar_Emulator is a Adafruit_DotStar LED strip emulator to speed up development of controller software.',
    long_description=long_description,
    author='Christopher Ross',
    author_email='chris.rossx@gmail.com',
    packages=["DotStar_Emulator", ],
    install_requires=[
        "pygame>=1.9.2a0",
        "blinker>=1.4",
        "pillow>=2.9.0",
    ],
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Emulators",
    ]
)
