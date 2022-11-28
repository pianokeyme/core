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

void selectiveWipe(uint32_t color, uint16_t start, uint16_t stop) {
  for(uint16_t i=start; i<stop; i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
  }
  strip.show();    //  Update strip to match
}

void initializeStrip() {
  colorBlink(GREEN, 200);
  colorWipe(BLACK);
  updatePianoSize(piano_size);
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
  if (piano_effect == Rainbow) {
    color = getColorWheel(note);
  }
  else if (piano_effect == Gradient) {
    color = getColorGradient(note);
  }
  else {
    color = piano_color;
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
  uint32_t color_red = getRGB(piano_color, 0);
  uint32_t color_green = getRGB(piano_color, 1);
  uint32_t color_blue = getRGB(piano_color, 2);
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

void updatePianoSize(uint8_t size) {
  updateRange(BLACK);
  piano_size = size;
  updateRange(BLUE);
}

void updateLEDShift(uint16_t shift) {
  updateRange(BLACK);
  ledShift = shift;
  updateBridgeNotes();
  updateRange(BLUE);
}

void updateRange(uint32_t color) {
  if (ledShift == 1) {
    strip.setPixelColor(0, color);
  }
  else if (ledShift > 1) {
    strip.setPixelColor(ledShift-1, color);
    strip.setPixelColor(ledShift-2, color);
    if (ledShift > 2) {
      selectiveWipe(BLACK, 0, ledShift-3);
    }
  }
  uint16_t lastLed = getLed(piano_size);
  if (!isBridgeNote(piano_size)) {
    lastLed++;
  }
  if (lastLed == LED_COUNT-2) {
    strip.setPixelColor(LED_COUNT-1, color);
  }
  else if (lastLed < LED_COUNT-2) {
    strip.setPixelColor(lastLed+1, color);
    strip.setPixelColor(lastLed+2, color);
    if (lastLed < LED_COUNT-3) {
      selectiveWipe(BLACK, lastLed+3, LED_COUNT-1);
    }
  }
}