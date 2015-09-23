from setuptools import setup

setup(
    name="DotStar_Emulator",
    version='0.1',
    # url='',
    description='DotStar_Emulator is a Adafruit_DotStar LED strip emulator to speed up development of controller software ',
    author='Christopher Ross',
    author_email='chris.rossx@gmail.com',
    # packages=["fbone"],
    # include_package_data=True,
    # zip_safe=False,
    install_requires=[
        "pygame>=1.9.2a0",
        "blinker>=1.4",
        "ProxyTypes>=0.9",
        "pillow>=2.9.0",
    ],
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
