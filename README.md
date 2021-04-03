# inkkeys
Details and instructions can be found on https://there.oughta.be/a/macro-keyboard

In contrast to most of my other projects, I decided to put this into its own repository as it is slightly more complex and I am hoping for community contributions.

If you have pull-requests, bug reports or want to contribute new case designs, please do not hesitate to open an issue. For generic discussions, "show and tell" and if you are looking for support for something that is not a problem in the code here, I would recommend [r/thereoughtabe on reddit](https://www.reddit.com/r/thereoughtabe/).

## Mac Install
Installing on the mac requires several dependencies, some of which are not apparent without a little digging. In order for the AppKit dependency to properly compile, you must be using Python 3.3.* or higher. Note that pulse audio is linux only, so it must be commented/removed from the python code. You will not be able to install the dependency. The following commands should mostly put everything in order to run the controller.py script.

    brew install pkg-config
    brew install cairo
    pip3 install pillow
    pip3 install pyserial
    pip3 install psutil
    pip3 install AppKit
    pip3 install pyobjc

## Common problems

### Display revision 2
Apparently, the original design used revision 1 of the display, while many newly ordered version are revision 2. There are a few differences and thankfully, [Corky402 made a good list of required changes on Reddit](https://www.reddit.com/r/arduino/comments/l4wxxf/the_hardware_is_assembled_and_passed_all_tests/gqovq1j?utm_source=share&utm_medium=web2x&context=3). 

**NOTE:** This fork already has the changes for revision 2 implemented.

Here is an excerpt of the original post for reference:
>If you want to test your display hooked to a Arduino or Raspberry Pi you need to run examples for the epd2in9_V2 not the epd2in9.
>
>To get this awesome project working there is no need to make any alterations to the PCB, just simply plumb the Waveshare up on the connectors as I describe, not as per Sebastian's original post.
>
>PCB Pin Waveshare wiring loom
>
>+5v Grey
>
>GND Brown
>
>DIN Blue
>
>CLK Yellow
>
>CS Orange
>
>DC Green
>
>RST Purple
>
>BUSY White
>
>In short you are swapping the RST & BUSY lines on the PCB.
>
>Next, go to your Arduino sketch. This is for the hardware-test script. Enable line numbering and go to line 43 which reads -
>
>GxEPD2_290 display(/*CS=*/ PIN_CS, /*DC=*/ PIN_DC, /*RST=*/ PIN_RST, /*BUSY=*/ PIN_BUSY);
>
>Change this to -
>
>GxEPD2_290_T94 display(/*CS=*/ PIN_CS, /*DC=*/ PIN_DC, /*RST=*/ PIN_RST, /*BUSY=*/ PIN_BUSY);
>
>Then go to settings.h
>
>Lines 2 - 7 need to be altered so change that section of code as follows -
>
>const byte PIN_DIN = 16;
>
>const byte PIN_CLK = 15;
>
>const byte PIN_CS = 19;
>
>const byte PIN_DC = 18;
>
>const byte PIN_RST = 10;
>
>const byte PIN_BUSY = 14;
>
>The sketch will then compile and when uploaded to the board you will get the Waveshare drawing all sorts of Austin Powers time machine circles that make your eyes spin! 

### Alternate Neopixels ###
If a different LED is substituted for the PL9823, the usage in the led.ino file and hardware-test.ino file may be different. For the APA106 LED, the NeoPixels are initialized this way:

    Adafruit_NeoPixel leds = Adafruit_NeoPixel(N_LED, PIN_LED, NEO_GRB + NEO_KHZ800);

**NOTE:** This fork already has the changes for APA106 LEDs implemented.
