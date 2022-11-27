void colorBlink(uint32_t color, int wait) {
  for (uint16_t i=0; i<3; i++) {
    colorWipe(BLACK);
    delay(wait);
    colorWipe(color);
    delay(wait);
  }
}

void colorWipe(uint32_t color) {
  for(uint16_t i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
  }
  strip.show();    //  Update strip to match
}

void initializeStrip() {
  colorBlink(GREEN, 200);
  colorWipe(BLACK);
  if (ledShift == 1) {
    strip.setPixelColor(ledShift-1, BLUE);
  }
  else if (ledShift > 1) {
    strip.setPixelColor(ledShift-1, BLUE);
    strip.setPixelColor(ledShift-2, BLUE);        
  }
  
  uint16_t lastLed = getLed(NUM_NOTES);
  if (!isBridgeNote(NUM_NOTES)) {
    lastLed++;
  }
  if (lastLed == LED_COUNT-2) {
    strip.setPixelColor(lastLed+1, BLUE);
  }
  else if (lastLed < LED_COUNT-2) {
    strip.setPixelColor(lastLed+1, BLUE);
    strip.setPixelColor(lastLed+2, BLUE);
  }
  strip.show();
}

void updateNote(uint8_t note, uint8_t value) {
  uint16_t led = getLed(note);
  uint32_t color = value == 0 ? BLACK : getNoteColor(note);
  strip.setPixelColor(led, color);
  if (!isBridgeNote(note)) {                  // note=36 -> led=71 , note=72 -> led=142 (ledShift = 2)
    strip.setPixelColor(led + 1, color);
  }
}

uint32_t getNoteColor(uint8_t note) {
  uint32_t color;
  if (notes_effect == Rainbow) {
    color = getColorWheel(note);
  }
  else if (notes_effect == Gradient) {
    color = getColorGradient(note);
  }
  else {
    color = notes_color;
  }
  return color;
}

uint32_t getColorWheel(uint8_t WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

uint32_t getColorGradient(uint8_t note) {
  uint32_t color;
  uint32_t color_red = getRGB(notes_color, 0);
  uint32_t color_green = getRGB(notes_color, 1);
  uint32_t color_blue = getRGB(notes_color, 2);
  if (color_red >= color_green && color_red >= color_blue) {
    color_green = (color_green + note > color_red) ? color_red : (color_green + note);
    color_blue  = (color_blue + note > color_red) ? color_red : (color_blue + note);
  }
  else if (color_green >= color_red && color_green >= color_blue) {
    color_red   = (color_red + note > color_green) ? color_green : (color_red + note);
    color_blue  = (color_blue + note > color_green) ? color_green : (color_blue + note);
  }
  else if (color_blue >= color_red && color_blue >= color_green) {
    color_red   = (color_red + note > color_blue) ? color_blue : (color_red + note);
    color_green = (color_green + note > color_blue) ? color_blue : (color_green + note);
  }
  color_red = color_red > 255 ? 255 : color_red;
  color_green = color_green > 255 ? 255 : color_green;
  color_blue = color_blue > 255 ? 255 : color_blue;
  color = strip.Color((uint8_t)color_red, (uint8_t)color_green, (uint8_t)color_blue);
  return color;
}

uint8_t getRGB(uint32_t color, uint8_t index) {
  uint32_t mask = 0xFF0000 >> (index*8);
  uint8_t basecolor = (color & mask) >> ((2-index)*8);
  return basecolor;
}

uint16_t getLed(uint8_t note) {
  // -1 for note to index conversion
  // *2 for two leds/key
  // ledShift to shift LEDs in strip
  uint16_t led = ((note-1) * 2) + ledShift;
  if (note > bridgeNote1) {
    led = --led;
  }
  if (note > bridgeNote2) {
    led = --led;
  }
  return led;
}

bool isBridgeNote(uint8_t note) {
  if (note != bridgeNote1 && note != bridgeNote2) {
    return false;
  }
  return true;
}

void updateBridgeNotes() {
  bridgeNote1 = 37 - floor(ledShift/2) - (ledShift%2);
  bridgeNote2 = bridgeNote1 + 36 + (ledShift%2);
}