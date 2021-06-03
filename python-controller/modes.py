#In here, the logic of the different modes are defined.
#Each mode has to implement four functions (use "pass" if not needed):
#
#- activate
#Called when the mode becomes active. Usually used to set up static key assignment and icons
#- poll
#Called periodically and typically used to poll a state which you need to monitor. At the end you have to return an interval in seconds before the function is to be called again - otherwise it is not called a second time
#- animate
#Called up to 30 times per second, used for LED animation
#- deactivate
#Called when the mode becomes inactive. Used to clean up callback functions and images on the screen that are outside commonly overwritten areas.

#To avoid multiple screen refreshs, the modules usually do not clean-up the display when being deactivvated. Instead, each module is supposed to set at least the area corresponding to each button (even if it needs to be set to white if unused).

from inkkeys import *
import time
from threading import Timer
from PIL import Image, ImageDraw, ImageFont
from colorsys import hsv_to_rgb


        ############# Simple example. For Blender we just set up a few key assignments with corresponding images.
        ## Blender ## To be honest: Blender is just the minimalistic example here. Blender is very keyboard centric
        ############# and you should get used to the real shortcuts as it is much more efficient to stay on the keyboard all the time.

class ModeBlender:

    def activate(self, device):
        device.sendTextFor("title", "Blender", inverted=True) #Title

        #Button1 (Jog dial press)
        device.sendTextFor(1, "<   Play/Pause   >")
        device.assignKey(KeyCode.SW1_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_SPACE, ActionCode.PRESS)]) #Play/pause
        device.assignKey(KeyCode.SW1_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_SPACE, ActionCode.RELEASE)])

        #Jog dial rotation
        device.assignKey(KeyCode.JOG_CW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_RIGHT)]) #CW = Clock-wise, one frame forward
        device.assignKey(KeyCode.JOG_CCW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT)]) #CCW = Counter clock-wise, one frame back

        #Button2 (top left)
        device.sendIconFor(2, "icons/camera-reels.png")
        device.assignKey(KeyCode.SW2_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_0, ActionCode.PRESS)]) #Set view to camera
        device.assignKey(KeyCode.SW2_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_0, ActionCode.RELEASE)])

        #Button3 (left, second from top)
        device.sendIconFor(3, "icons/person-bounding-box.png")
        device.assignKey(KeyCode.SW3_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_DIVIDE, ActionCode.PRESS)]) #Isolation view
        device.assignKey(KeyCode.SW3_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_DIVIDE, ActionCode.RELEASE)])

        #Button4 (left, third from top)
        device.sendIconFor(4, "icons/dot.png")
        device.assignKey(KeyCode.SW4_PRESS, []) #Not used, set to nothing.
        device.assignKey(KeyCode.SW4_RELEASE, [])

        #Button5 (bottom left)
        device.sendIconFor(5, "icons/dot.png")
        device.assignKey(KeyCode.SW5_PRESS, []) #Not used, set to nothing.
        device.assignKey(KeyCode.SW5_RELEASE, [])

        #Button6 (top right)
        device.sendIconFor(6, "icons/aspect-ratio.png")
        device.assignKey(KeyCode.SW6_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_DOT, ActionCode.PRESS)]) #Center on selection
        device.assignKey(KeyCode.SW6_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEYPAD_DOT, ActionCode.RELEASE)])

        #Button7 (right, second from top)
        #Button4 (left, third from top)
        device.sendIconFor(7, "icons/collection.png")
        device.assignKey(KeyCode.SW7_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F12), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE)]) #Render sequence
        device.assignKey(KeyCode.SW7_RELEASE, [])

        #Button8 (right, third from top)
        device.sendIconFor(8, "icons/dot.png")
        device.assignKey(KeyCode.SW8_PRESS, []) #Not used, set to nothing.
        device.assignKey(KeyCode.SW8_RELEASE, [])

        #Button9 (bottom right)
        device.sendIconFor(9, "icons/dot.png")
        device.assignKey(KeyCode.SW9_PRESS, []) #Not used, set to nothing.
        device.assignKey(KeyCode.SW9_RELEASE, [])

        device.updateDisplay()

    def poll(self, device):
        return False    # No polling in this example

    def animate(self, device):
        device.fadeLeds() #No LED animation is used in this mode, but we call "fadeLeds" anyway to fade colors that have been set in another mode before switching

    def deactivate(self, device):
        pass            # Nothing to clean up in this example




        ##########
        ## Gimp ## The Gimp example is similar to Blender, but we add a callback to pressing the jog dial to switch functions
        ##########

class ModeGimp:
    jogFunction = ""    #Keeps track of the currently selected function of the jog dial

    def activate(self, device):
        device.sendTextFor("title", "Gimp")  #Title

        #Button2 (top left)
        device.sendIconFor(2, "icons/fullscreen.png")
        device.assignKey(KeyCode.SW2_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_B), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_Z)]) #Cut to selection (this shortcut appears to be language dependent, so you will probably need to change it)
        device.assignKey(KeyCode.SW2_RELEASE, [])

        #Button3 (left, second from top)
        device.sendIconFor(3, "icons/upc-scan.png")
        device.assignKey(KeyCode.SW3_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_B), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_I)]) #Cut to content (this shortcut appears to be language dependent, so you will probably need to change it)
        device.assignKey(KeyCode.SW3_RELEASE, [])

        #Button4 (left, third from top)
        device.sendIconFor(4, "icons/crop.png")
        device.assignKey(KeyCode.SW4_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_B), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_L)]) #Canvas size (this shortcut appears to be language
        device.assignKey(KeyCode.SW4_RELEASE, [])

        #Button5 (bottom left)
        device.sendIconFor(5, "icons/arrows-angle-expand.png")
        device.assignKey(KeyCode.SW5_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_B), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_ALT, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_S)]) #Resize (this shortcut appears to be language
        device.assignKey(KeyCode.SW5_RELEASE, [])

        #Button6 (top right)
        device.sendIconFor(6, "icons/clipboard-plus.png")
        device.assignKey(KeyCode.SW6_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_V), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.RELEASE)]) #Paste as new image
        device.assignKey(KeyCode.SW6_RELEASE, [])

        #Button7 (right, second from top)
        device.sendIconFor(7, "icons/layers-half.png")
        device.assignKey(KeyCode.SW7_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_N), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.RELEASE)]) #New layer
        device.assignKey(KeyCode.SW7_RELEASE, [])

        #Button8 (right, third from top)
        device.sendIconFor(8, "icons/arrows-fullscreen.png")
        device.assignKey(KeyCode.SW8_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_J), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT, ActionCode.RELEASE)]) #Zom to fill screen
        device.assignKey(KeyCode.SW8_RELEASE, [])

        #Button9 (bottom right)
        device.sendIconFor(9, "icons/dot.png")
        device.assignKey(KeyCode.SW9_PRESS, []) #Not used, set to nothing.
        device.assignKey(KeyCode.SW9_RELEASE, [])





        #Button 1 / jog dial press
        device.assignKey(KeyCode.SW1_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F15, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW1_RELEASE, [])
        
        device.updateDisplay()      #Everything has been sent to the display. Time to refresh it.

    def poll(self, device):
        return False #Nothing to poll

    def animate(self, device):
        device.fadeLeds() #No LED animation is used in this mode, but we call "fadeLeds" anyway to fade colors that have been set in another mode before switching

    def deactivate(self, device):
        device.clearCallbacks() #Remove our callbacks if we switch to a different mode




        ############## This mode is used as a fallback and a much more complex example than Gimp. It also uses a switchable Jog dial,
        ## Fallback ## but most of its functions give a feedback via LED. Also, we use MQTT (via a separately defined class) to get
        ############## data from a CO2 sensor and control a light (both including feedback)

class ModeFallback:
    lightState = None   #Current state of the lights in my office. (Keeping track to know when to update the screen)
    demoActive = False  #We have a demo button and this keeps track whether the demo mode is active, so we know when to update the screen

    def activate(self, device):
        device.sendTextFor("title", "Default") #Title

        #Jog dial rotation
        device.assignKey(KeyCode.JOG_CW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_RIGHT)]) #CW = Clock-wise, one frame forward
        device.assignKey(KeyCode.JOG_CCW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT)]) #CCW = Counter clock-wise, one frame back

        #Button 1 / jog dial press
        device.assignKey(KeyCode.SW1_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F15, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW1_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F15, ActionCode.RELEASE)])

        ### Button 2 ###
        device.sendIconFor(2, "icons/app-docker.png", centered=False)
        device.assignKey(KeyCode.SW2_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_1, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW2_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_1, ActionCode.RELEASE)])
        #device.sendTextFor(2, "Docker", inverted=False) #Title
        
        ### Button 3 ###
        device.sendIconFor(3, "icons/app-dash.png", centered=False)
        device.assignKey(KeyCode.SW3_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_2, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW3_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_2, ActionCode.RELEASE)])
        
        ### Button 4 ###
        device.sendIconFor(4, "icons/app-postman.png", centered=False)
        device.assignKey(KeyCode.SW4_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_3, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW4_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_3, ActionCode.RELEASE)])
        
        ### Button 5 ###
        device.sendIconFor(5, "icons/app-bitwarden.png", centered=False)
        device.assignKey(KeyCode.SW5_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_4, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW5_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_4, ActionCode.RELEASE)])

        ### Button 6 ###
        device.sendIconFor(6, "icons/app-slack.png", centered=False)
        device.assignKey(KeyCode.SW6_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_5, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW6_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_5, ActionCode.RELEASE)])

        ### Button 7 ###
        device.sendIconFor(7, "icons/app-chrome.png", centered=False)
        device.assignKey(KeyCode.SW7_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_6, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW7_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_6, ActionCode.RELEASE)])

        ### Button 8 ###
        device.sendIconFor(8, "icons/app-outlook.png", centered=False)
        device.assignKey(KeyCode.SW8_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_7, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW8_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_7, ActionCode.RELEASE)])

        ### Button 9 ###
        device.sendIconFor(9, "icons/app-vscode.png", centered=False)
        device.assignKey(KeyCode.SW9_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_8, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW9_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_8, ActionCode.RELEASE)])
        ### All set, let's update the display ###

        device.updateDisplay()

    #Called to update the icon of button 4, showing the state of the office light (as if I couldn't see it in the real room, but it is a nice touch to update the display accordingly)
    def showLightState(self, device, update=True):
        if self.lightState:
            device.sendIconFor(4, "icons/lightbulb.png", centered=(not self.demoActive))
        else:
            device.sendIconFor(4, "icons/lightbulb-off.png", centered=(not self.demoActive))
        if update:
            device.updateDisplay()

    def animate(self, device):
        if self.demoActive: #In demo mode, we animate the LEDs here
            def rgbTupleToInt(rgb):
                return (int(rgb[0]*255) << 16) | (int(rgb[1]*255) << 8) | int(rgb[2]*255)

            t = time.time()
            leds = [rgbTupleToInt(hsv_to_rgb(t + i/device.nLeds, 1, 1)) for i in range(device.nLeds)]
            device.setLeds(leds)
        else:               #If not in demo mode, we call "fadeLeds" to create a fade animation for any color set anywhere in this mode
            device.fadeLeds()

    def poll(self, device):
        return False    #No polling required

    def animate(self, device):
        pass    #In this mode we want permanent LED illumination. Do not fade or animate otherwise.

    def deactivate(self, device):
        device.clearCallbacks() #Clear our callbacks if we switch to a different mode

    def poll(self, device):
        if device.status == "Error":
            device.sendLedAnimation(2, 50, 20, r=255, iteration=10)
        if device.status == "Warning":
            device.sendLedAnimation(2, 50, 20, r=247, g=160, b=0, iteration=10)
        if device.status == "Done":
            device.sendLedAnimation(2, 50, 20, g=255, iteration=2)
        if device.status == "Working":
            device.sendLedAnimation(2, 50, 20, r=0, g=156, b=247, iteration=10)
        if device.status:
            device.setStatus("")
        return 1 

class ModeMiniFallback:

    def activate(self, device):
        device.sendTextFor("title", "Mac-Mini") #Title

        #Jog dial rotation
        device.assignKey(KeyCode.JOG_CW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_RIGHT)]) #CW = Clock-wise, one frame forward
        device.assignKey(KeyCode.JOG_CCW, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_SHIFT), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT)]) #CCW = Counter clock-wise, one frame back

        #Button 1 / jog dial press
        device.assignKey(KeyCode.SW1_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F15, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW1_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F15, ActionCode.RELEASE)])

        ### Button 2 ###
        device.sendIconFor(2, "icons/app-brave.png", centered=False)
        device.assignKey(KeyCode.SW2_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F1, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW2_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F1, ActionCode.RELEASE)])
        #device.sendTextFor(2, "Docker", inverted=False) #Title
        
        ### Button 3 ###
        device.sendIconFor(3, "icons/app-email.png", centered=False)
        device.assignKey(KeyCode.SW3_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F2, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW3_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F2, ActionCode.RELEASE)])
        
        ### Button 4 ###
        device.sendIconFor(4, "icons/app-messenger.png", centered=False)
        device.assignKey(KeyCode.SW4_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F3, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW4_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F3, ActionCode.RELEASE)])
        
        ### Button 5 ###
        device.sendIconFor(5, "icons/app-bitwarden.png", centered=False)
        device.assignKey(KeyCode.SW5_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_4, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW5_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_4, ActionCode.RELEASE)])

        ### Button 6 ###
        device.sendIconFor(6, "icons/app-pages.png", centered=False)
        device.assignKey(KeyCode.SW6_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F5, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW6_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F5, ActionCode.RELEASE)])

        ### Button 7 ###
        device.sendIconFor(7, "icons/app-keynote.png", centered=False)
        device.assignKey(KeyCode.SW7_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F6, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW7_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F6, ActionCode.RELEASE)])

        ### Button 8 ###
        device.sendIconFor(8, "icons/app-dash.png", centered=False)
        device.assignKey(KeyCode.SW8_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F7, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW8_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_F7, ActionCode.RELEASE)])

        ### Button 9 ###
        device.sendIconFor(9, "icons/app-vscode.png", centered=False)
        device.assignKey(KeyCode.SW9_PRESS, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.PRESS), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_8, ActionCode.PRESS)])
        device.assignKey(KeyCode.SW9_RELEASE, [event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_CTRL, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_LEFT_WINDOWS, ActionCode.RELEASE), event(DeviceCode.KEYBOARD, KeyboardKeycode.KEY_8, ActionCode.RELEASE)])
        ### All set, let's update the display ###

        device.updateDisplay()

    def poll(self, device):
        if device.status == "Error":
            device.sendLedAnimation(2, 50, 20, r=255, iteration=10)
        if device.status == "Warning":
            device.sendLedAnimation(2, 50, 20, r=247, g=160, b=0, iteration=10)
        if device.status == "Done":
            device.sendLedAnimation(2, 50, 20, g=255, iteration=2)
        if device.status == "Working":
            device.sendLedAnimation(2, 50, 20, r=0, g=156, b=247, iteration=10)
        if device.status:
            device.setStatus("")
        return 1    

    def animate(self, device):
        pass    #In this mode we want permanent LED illumination. Do not fade or animate otherwise.

    def deactivate(self, device):
        device.clearCallbacks() #Clear our callbacks if we switch to a different mode

