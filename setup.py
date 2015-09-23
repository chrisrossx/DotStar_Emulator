from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DotStar_Emulator', 'emulator', 'media', 'about.txt')) as f:
    long_description = f.read()


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
