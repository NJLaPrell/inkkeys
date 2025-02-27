SERIALPORT = None #None = Auto-detect, to specify a specific serial port, you can set it to something like "/dev/ttyACM0" (Linux) or "COM1" (Windows)
VID = 0x1B4F      #USB Vendor ID for a Pro Micro
PID = 0x9206    #USB Product ID for a Pro Micro
DEBUG = True     #More output on the command line
HTTP_PORT = 8080

from inkkeys import *        #Inkkeys module
from processchecks import *  #Functions to check for active processes and windows
from modes import *          #Definitions of the hotkey functions in different "modes"

import time                         #Time functions
from serial import SerialException  #Serial functions
import serial.tools.list_ports      #Function to iterate over serial ports
import re                           #Regular expressions process name matching
import traceback                    #Print tracebacks if an error is thrown and caught
import socket                       #Get the hostname of the computer

import json
import threading                    #Run an http server in a separate thread.
from http.server import HTTPServer, BaseHTTPRequestHandler
from json import JSONDecodeError

print("https://there.oughta.be/a/macro-keyboard")
print('I will try to stay connected. Press Ctrl+c to quit.')

class HttpHandler(BaseHTTPRequestHandler):  
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        if DEBUG:
            print(f"POST - {content_length} bytes received.")
        try:
            payload = json.loads(str(post_data, "utf-8"))
            if "status" in payload:
                device.setStatus(payload["status"])

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
        except JSONDecodeError as jde:
            print(jde)
            print(post_data)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

def listenToHttp():
    print(f'Listening for http traffic on port {HTTP_PORT}')
    try:
        httpd = HTTPServer(("0.0.0.0", HTTP_PORT), HttpHandler)
        httpd.serve_forever()
    except OSError:
        print(f"Cannot bind http server on adress {HTTP_PORT}")

httpThread = threading.Thread(target=listenToHttp, daemon=True)
httpThread.start()



############################################################################################################

#This is the main part, which reassigns keys, sets the content of the display and updates the LEDs.
#The logic of this is built around "modes". The modes themselves are defined in "modes.py", where you can
#change key assignments, images, LED animations and their entire logic.

#Below, you only define a list of modes (defined in "modes.py") that are active and set either a process
#(mode would be active whenever the process runs) or an active window (mode is active if the window has
#the focus. The latter is a compiled regular expression pattern. Mode priority corresponds to the order in the
#list, so the first mode with a matching process or active window will be activated.

modes = [\
            {"mode": ModeBlender(), "activeWindow": re.compile("^Blender")}, \
            {"mode": ModeGimp(), "activeWindow": re.compile("^GIMP.*")}, \
            {"mode": ModeMiniFallback(), "hostname": re.compile("^Mac-Min.*")}, \
            {"mode": ModeFallback()} \
        ]

hostname = socket.gethostname()

############################################################################################################

# Usually there should not be anything to be customized below this point

############################################################################################################

#If we found the device, successfully connected and retreived its information, we enter this work function,
#which primarily consists of an infinite loop that only returns if we hit Ctrl+C (or kill the process).

def work():
    mode = None             #Current mode of the device (i.e. key mappings for specific process).
    pollInterval = 0        #Polling interval as requested by the module when the last call to "poll" was made
    lastPoll = 0            #Keeps track of the last time the poll function of the mode instance was called
    lastProcessList = 0     #Keeps track of the last time the list of processes was retrieved
    lastModeCheck = 0       #Keeps track of the last time the current window was checked and a decision about the mode was made
    activeWindow = None
    
    try:
        while True:     #Now we are in our main, infinite loop -------------------
            now = time.time() #Time of this iteration

            if now - lastProcessList > 5.0:      # Only check the process list every 5 seconds.
                processes = getActiveProcesses() # This is a surprisingly expensive and slow call, so don't overdo as it might prevent smooth LED animation (fixable by implementing a second thread) and burn more CPU resources than you might want from a background process
                lastProcessList = now

            if now - lastModeCheck > 0.5:       # Check active window and decide which mode to use. This can be done more regularly, but since the e-ink screen takes a moment to update, it does not make sense to check more frequently
                window = getActiveWindow()      # Get the currently active window
                if window != None:              # Sometime getting the active window fails, then ignore it. (Some window managers allow having no window in focus)
                    if DEBUG and activeWindow != window:                   #Enable DEBUG to see the actual name of the current window if you need it to match your modules
                        print("Active window: " + str(window))
                    activeWindow = window

                for i in modes:                 #Iterate over modes and use the first one that matches
                    if ("process" in i and i["process"] in processes) or ("hostname" in i and i["hostname"].match(hostname)) or ("activeWindow" in i and i["activeWindow"].match(activeWindow)) or not ("process" in i or "activeWindow" in i or "hostname" in i):
                        #Either the process for this mode is running or the active window matches the regular expression. This is the mode we will set now.
                        if i["mode"] != mode:           # Do not set the mode again if we already have this one
                            if mode != None:            
                                mode.deactivate(device) # If there was a previous mode, call its deactivate function
                                device.sendLedAnimation(2, 50, 20, b=255, iteration=2)
                                device.resetDisplay()
                            mode = i["mode"]            # Set new mode
                            mode.activate(device)       # ...and call its activate function
                            pollInterval = 0            # Reset the poll intervall to call mode.poll() at least once (see below)
                        break
                lastModeCheck = now

            if pollInterval >= 0 and now - lastPoll > pollInterval:    #Regularly call the poll function of the mode if it requires regular polling
                #The poll function returns the desired interval when it should be called next - or False if polling is not required in this mode
                pollInterval = mode.poll(device)
                lastPoll = now

            #Now for the functions that need to be called very often and fast:
            mode.animate(device)    #Used for LED animations
            device.poll()           #Required for the callbacks that are associated with key presses reported via serial

            #If the actions so far did take less than 1/30 seconds, sleep until 1/30s have passed as there is no need to exceed 30fps
            timeTo30fps = time.time() - now + 0.0333
            if timeTo30fps > 0:
                time.sleep(timeTo30fps)
                    #End of main loop -------------------------------------------


    except KeyboardInterrupt:       #User pressed Ctrl+c
        #mqtt.disconnect()
        print('Disconnected from device. Hit Ctrl+c again to quit before reconnect.')


#Try connecting on the given port and work with it.
#Will return false if connection fails or an unknown device is present.
#If it succeeds, it will enter the main working loop forever. It will only return if an error occurs and return True to report that it was working with the correct device.
def tryUsingPort(port):
    try:
        if device.connect(port):
            print(f"Connected to controller on {socket.gethostname()}")
            device.resetDisplay()
            work()  #Success, enter main loop
            device.disconnect()
            return True
    except SerialException as e:
        print("Serial error: ", e)
    except:
        #Something entirely unexpected happened. We will catch it nevertheless, so the device keeps working as this process will probably run in the background unsupervised. But we need to print a proper stacktrace, so we can debug the problem.
        if DEBUG:
            print(traceback.format_exc())
        print("Error: ", sys.exc_info()[0])
    return False

# Instantiate the device
device = Device()
device.debug = DEBUG
try:
    while True:
        if SERIALPORT != None:  #Explicit port has been defined
            tryUsingPort(SERIALPORT)
        else:                   #No explicit port defined. Search for the device
            for port in serial.tools.list_ports.comports(): #Iterate over all serial ports
                if port.vid != VID or port.pid != PID:
                    continue                                #Skip if vendor or product ID do not match
                if tryUsingPort(port.device):               #Try connecting to this device
                    break                                   #Connection was successful and inkkeys was found. If we reach this point, we do not need to search on another port. We got disconnected or some other kind of error, so skip the rest of the port list and start over.
        print("I will retry in three seconds...")
        time.sleep(3)
except KeyboardInterrupt:       #User pressed Ctrl+c
    print('Ok, bye.')


