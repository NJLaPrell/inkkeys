from .protocol import *
import serial
import time
import io
from threading import Lock
from PIL import Image, ImageDraw, ImageOps, ImageFont
from serial import SerialException  #Serial functions

CHUNK_SIZE = 100

class Device:
    ser = None
    inbuffer = ""

    awaitingResponseLock = Lock()

    testmode = False
    nLeds = 0
    dispW = 0
    dispH = 0
    rotFactor = 0
    rotCircleSteps = 0

    bannerHeight = 20 #Defines the height of top and bottom banner

    imageBuffer = []

    callbacks = {} #This object stores callback functions that react directly to a keypress reported via serial

    ledState = None         #Current LED status, so we can animate them over time
    ledTime = None          #Last time LEDs were set

    debug = True;

    def connect(self, dev):
        print("Connecting to ", dev, ".")
        self.ser = serial.Serial(dev, 115200, timeout=1, write_timeout=5)
        if not self.requestInfo(3):
            self.disconnect()
            return False
        if self.testmode:
            print("Connection to ", self.ser.name, " was successfull, but the device is running the hardware test firmware, which cannot be used for anything but testing. Please flash the proper inkkeys firmware to use it.")
            return False
        print("Connected to ", self.ser.name, ".")
        return True

    def disconnect(self):
        if self.ser != None:
            self.ser.close()
            self.ser = None

    def sendToDevice(self, command):
        if self.debug:
            print("Sending: " + command)
        self.ser.write((command + "\n").encode())

    def sendBinaryToDevice(self, data):
        if self.debug:
            print("Sending " + str(len(data)) + " bytes of binary data.")
        try:
            # Send binary data in chunks to prevent killing the serial connection
            start = time.time()
            endIx = CHUNK_SIZE
            startIx = 0
            while (startIx < len(data)):
                self.ser.write(data[startIx:endIx])
                #if self.debug:
                #    print(data[startIx:endIx].hex())
                startIx = startIx + CHUNK_SIZE
                endIx = endIx + CHUNK_SIZE
            if self.debug:
                print("Data sent.")
        except SerialException as e:
            print("Serial error: ", e)

    def readFromDevice(self):
        if self.ser.in_waiting > 0:
            self.inbuffer += self.ser.read(self.ser.in_waiting).decode("ISO-8859-16").replace("\r", "")
        chunks = self.inbuffer.split("\n", 1)
        if len(chunks) > 1:
            cmd = chunks[0]
            self.inbuffer = chunks[1]
            if self.debug:
                print("Received: " + cmd)
            return cmd
        return None

    def poll(self):
        with self.awaitingResponseLock:
            input = self.readFromDevice()
        if input != None:
            if input[0] == KeyCode.JOG.value and (input[1:].isdecimal() or (input[1] == '-' and input[2:].isdecimal())):
                if KeyCode.JOG.value in self.callbacks:
                    self.callbacks[KeyCode.JOG.value](int(input[1:]))
            elif input in self.callbacks:
                self.callbacks[input]()

    def registerCallback(self, cb, key):
        self.callbacks[key.value] = cb

    def clearCallback(self, key):
        if key.value in self.callbacks:
            del self.callbacks[key.value]

    def clearCallbacks(self):
        self.callbacks = {}

    def assignKey(self, key, sequence):
        self.sendToDevice(CommandCode.ASSIGN.value + " " + key.value + (" " + " ".join(sequence) if len(sequence) > 0 else ""))

    def sendLed(self, colors):
        self.sendToDevice(CommandCode.LED.value + " " + " ".join(colors))

    def requestInfo(self, timeout):
        with self.awaitingResponseLock:
            print("Requesting device info...")
            start = time.time()
            self.sendToDevice(CommandCode.INFO.value)
            line = self.readFromDevice()
            while line != "Inkkeys":
                if time.time() - start > timeout:
                    return False
                if line == None:
                    time.sleep(0.1)
                    line = self.readFromDevice()
                    continue
                print("Skipping: ", line)
                line = self.readFromDevice()
            print("Header found. Waiting for infos...")
            line = self.readFromDevice()
            while line != "Done":
                if time.time() - start > timeout:
                    return False
                if line == None:
                    time.sleep(0.1)
                    line = self.readFromDevice()
                    continue
                if line.startswith("TEST "):
                    self.testmode = line[5] != "0"
                elif line.startswith("N_LED "):
                    self.nLeds = int(line[6:])
                elif line.startswith("DISP_W "):
                    self.dispW = int(line[7:])
                elif line.startswith("DISP_H "):
                    self.dispH = int(line[7:])
                elif line.startswith("ROT_CIRCLE_STEPS "):
                    self.rotCircleSteps = int(line[17:])
                else:
                    print("Skipping: ", line)
                line = self.readFromDevice()
            print("End of info received.")
            print("Testmode: ", self.testmode)
            print("Number of LEDs: ", self.nLeds)
            print("Display width: ", self.dispW)
            print("Display height: ", self.dispH)
            print("Rotation circle steps: ", self.rotCircleSteps)
            return True

    # Send the image to the controller
    def sendImage(self, x, y, image):
        if self.debug:
            print(f"sendImage({x}, {y})")
        self.imageBuffer.append({"x": x, "y": y, "image": image.copy()})
        w, h = image.size
        data = image.convert("1").rotate(180).tobytes()
        self.sendToDevice(CommandCode.DISPLAY.value + " " + str(x) + " " + str(y) + " " + str(w) + " " + str(h))
        self.sendBinaryToDevice(data)
        return True

    # Resends all of the images from the buffer to the controller so they can be buffered in the display.
    def resendImageData(self):
        if self.debug:
            print("resendImageData()")
        for part in self.imageBuffer:
            image = part["image"]
            x = part["x"]
            y = part["y"]
            w, h = image.size
            data = image.convert("1").rotate(180).tobytes()
            self.sendToDevice(CommandCode.DISPLAY.value + " " + str(x) + " " + str(y) + " " + str(w) + " " + str(h))
            self.sendBinaryToDevice(data)
        self.imageBuffer = []

    # Blanks out the display
    def resetDisplay(self):
        self.sendToDevice('R r')

    # Render the images on the display
    def updateDisplay(self, fullRefresh=False, timeout=5):
        with self.awaitingResponseLock:
            if self.debug:
                print(f"updateDisplay(fullRefresh={fullRefresh}, timeout={timeout})")
            # Send the refresh command and wait for "ok" response until the timeout is up.
            start = time.time()
            self.sendToDevice(CommandCode.REFRESH.value + " " + (RefreshTypeCode.FULL.value if fullRefresh else RefreshTypeCode.PARTIAL.value))
            line = self.readFromDevice()
            while line != "ok":
                if time.time() - start > timeout:
                    if self.debug:
                        print("Timed out...")
                    return False
                if line == None:
                    time.sleep(0.1)
                    line = self.readFromDevice()
                    continue
                line = self.readFromDevice()
            # Resend all of the image data from the buffer to buffer in the display
            self.resendImageData()
            self.sendToDevice(CommandCode.REFRESH.value + " " + RefreshTypeCode.OFF.value)
            start = time.time()
            line = self.readFromDevice()
            while line != "ok":
                if time.time() - start > timeout:
                    if self.debug:
                        print("Timed out...")
                    return False
                if line == None:
                    time.sleep(0.1)
                    line = self.readFromDevice()
                    continue
                line = self.readFromDevice()

    # Get the area for the image that is being sent.
    def getAreaFor(self, function):
        bannerSpace = self.bannerHeight//2 #Each side gives space for half the banner height
        tileH = self.dispH//4 #Tile height is the screen height divided by 4
        tileW = (self.dispW//2)-bannerSpace #Tile width is half the screen minus half the banner height 
                
        if function == "title":
            # TODO: The controler hangs and fails to upddate the display when the title is less than 40 in height
            area = (tileW, 0, 40, self.dispH)
        elif function == 1:
            # TODO: Decide what to do with button 1 text, if anything.
            area = (0, tileW, self.dispH, self.dispW//2+self.bannerHeight)
        elif function <= 5:
            area = (tileW+(self.bannerHeight), (5-function)*tileH, tileW+2, tileH)
        else:
            area = (0, (9-function)*tileH, tileW+2, tileH)
        
        if self.debug:
            x, y, w, h = area
            print(f"Area is {x}/{y} {w}x{h}")
        return area

    # Resize the image if needed and send it to the controller.
    def sendImageFor(self, function, image):
        x, y, w, h = self.getAreaFor(function)
        if (w, h) != image.size:
            if self.debug:
                print("Rescaling image from " + str(image.size) + " to " + str((w, h)) + ".")
            image = image.resize((w, h))
        self.sendImage(x, y, image)

    # Generate an image with text
    # TODO: Re-impliment text in place of icons. Currently only supports title
    def sendTextFor(self, function, text, subtext="", inverted=False):
        if self.debug:
            print(f"sendTextFor({function}, {text}, subtext={subtext}, inverted={inverted})")
        x, y, w, h = self.getAreaFor(function)
        font = ImageFont.truetype("font/Munro.ttf", 10)
        fW, fH = font.getsize(text);
        img = Image.new("1", (h, w), color=(0 if inverted else 1))
        ImageDraw.Draw(img).text((h//2,(w-fH)//2), text, anchor="mt", font=font, fill=(1 if inverted else 0)) #Center the text on image
        self.sendImageFor(function, img.rotate(270, expand=1))

    # Generate and send the icon to the controller
    # TODO: Re-impliment marked/crossed overlays
    def sendIconFor(self, function, icon, inverted=False, centered=True, marked=False, crossed=False):
        if self.debug:
            print(f"sendIconFor({icon}, inverted={inverted}, centered={centered}, marked={marked}, crossed={crossed})")
        x, y, w, h = self.getAreaFor(function)
        img = Image.new("1", (w, h), color=(0 if inverted else 1))
        imgIcon = Image.open(icon).convert("RGB").rotate(270, expand=True)
        if inverted:
            imgIcon = ImageOps.invert(imgIcon)
        wi, hi = imgIcon.size
        if function < 6:
            pos = (0, (h - wi)//2)
        else:
            pos = ((w - hi), (h - wi)//2)
        img.paste(imgIcon, pos)

        #if marked:
        #    imgMarker = Image.open("icons/chevron-compact-right.png" if function < 6 else "icons/chevron-compact-left.png")
        #    wm, hm = imgMarker.size
        #    img.paste(imgMarker, (-16,(h - hm)//2) if function < 6 else (w-wm+16,(h - hm)//2), mask=ImageOps.invert(imgMarker.convert("RGB")).convert("1"))

        #if crossed:
        #    d = ImageDraw.Draw(img)
        #    d.line([pos[0]+5, pos[1]+5, pos[0]+wi-5, pos[1]+hi-5], width=3)
        #    d.line([pos[0]+5, pos[1]+hi-5, pos[0]+wi-5, pos[1]+5], width=3)

        self.sendImage(x, y, img)

    # Set LEDs to a color.
    def setLeds(self, leds):
        ledStr = ['{:06x}'.format(i) for i in leds]
        self.ledTime = time.time()
        self.ledState = leds
        self.sendLed(ledStr)

    def fadeLeds(self):
        if self.ledState == None:
            return
        p = (3.5 - (time.time() - self.ledTime))/0.5 #Stay on for 3 seconds and then fade out over 0.5 seconds
        if p >= 1:
            return
        if p <= 0:
            self.ledState = None
            self.sendLed(["000000" for i in range(self.nLeds)])
            return
        dimmedLeds = [(int((i & 0xff0000) * p) & 0xff0000) | (int((i & 0xff00) * p) & 0xff00) | (int((i & 0xff) * p) & 0xff) for i in self.ledState]
        ledStr = ['{:06x}'.format(i) for i in dimmedLeds]
        self.sendLed(ledStr)

