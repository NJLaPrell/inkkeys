/*
 * E-Ink adaptive macro keyboard
 * See https://there.oughta.be/a/macro-keyboard
 * 
 * This part contains LED related functions
 */

//LEDs
Adafruit_NeoPixel leds = Adafruit_NeoPixel(N_LED, PIN_LED, NEO_GRB + NEO_KHZ800);

int steps;
int stepsRemaining = 0;
uint8_t stepDelay = 0;
unsigned long lastUpdate = 0;
int animation = 0;
int brightness = 0;
uint32_t color;
int iteration = 0;

void initLEDs() {
  leds.begin();
  leds.setBrightness(100);
  leds.clear();
  leds.show();
  //IMPORTANT: The original hardware design cannot provide enough
  //           current to set all LEDs to full white. If you want to
  //           increase the brightness, you have to consider their
  //           maximum current draw and either adapt the hardware
  //           design or the animations accordingly (i.e. do not
  //           allow for white color).
}

//Returns a darker version of color, dimmed to brightness/255
uint32_t dimmedColor(uint32_t color, byte brightness) {
  return (((color & 0xff0000) * brightness / 255) & 0xff0000)
       | (((color & 0x00ff00) * brightness / 255) & 0x00ff00)
       | (((color & 0xff) * brightness / 255) & 0x0000ff);
}

//Returns fully saturated color by hue (0..255)
uint32_t hue2rgb(int hue) {
  uint32_t r = constrain(abs( hue        % 256 * 6 - 765) - 255, 0, 255);
  uint32_t g = constrain(abs((hue + 85)  % 256 * 6 - 765) - 255, 0, 255);
  uint32_t b = constrain(abs((hue + 170) % 256 * 6 - 765) - 255, 0, 255);
  return r << 16 | g << 8 | b;
}

void animateLeds(int a, int s, int d, int br, uint32_t c, int i) {
  // A new animation is called.
  if (a != animation) {
    leds.clear();
    leds.show();
    steps = s;
    stepsRemaining = s;
    stepDelay = d;
    animation = a;
    brightness = br;
    color = c;
    iteration = i;
  } 

  if (a == animation) {
    if (stepsRemaining == 0 && iteration > 1) {
      stepsRemaining = steps;
      iteration--;
    }
    if (stepsRemaining == 0) {
      // Reset and turn animation off
      steps = 0;
      animation = 0;
      stepDelay = 0;
      leds.clear();
      leds.show();
    } else {
      // Call the animation function.
      switch (a) {
        case 1:
          ledGreeting();
          break;
        case 2:
          ledBlink();
          break;
       
      }
    } 
  }
  
  
}

// 1 - Short rainbow swirl on the LEDs as a greeting
void ledGreeting() {
  int i = steps - stepsRemaining;
  byte brightness = constrain(steps/2 - abs(i-steps/2), 0, 255);
  for (int j = 0; j < N_LED; j++) {
    leds.setPixelColor(j, dimmedColor(hue2rgb(i/2 + j*256/N_LED), brightness));
  }
  leds.show();
}

// 2 - Blink the LED blue
void ledBlink() {
  int i = steps - stepsRemaining;
  int brightness = constrain(steps/2 - abs(i-steps/2), 0, 255);
  for (int j = 0; j < N_LED; j++) {
    leds.setPixelColor(j, color);
    leds.setBrightness(brightness);
  }
  leds.show();
}

// Process the next step of any animation in progress.
void processAnimation() {
  if (animation > 0) {
    unsigned long now = millis();
    if (now > lastUpdate+stepDelay) {
      animateLeds(animation, steps, stepDelay, brightness, color, iteration);
      lastUpdate = now;
      stepsRemaining--;
    }
  }
}
