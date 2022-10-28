void colorBlink(uint32_t color, int wait) {
  for (int i=0; i<3; i++) {
    colorWipe(color);
    delay(wait);
    colorWipe(strip.Color(0,0,0));
    delay(wait);
  }
}

void colorWipe(uint32_t color) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
  }
  strip.show();    //  Update strip to match
}

void initializeStrip() {
  colorBlink(strip.Color(0,100,0), 200);
  if (ledShift == 1) {
    strip.setPixelColor(ledShift-1, strip.Color(0,0,50));
  }
  else if (ledShift > 1) {
    strip.setPixelColor(ledShift-1, strip.Color(0,0,50));
    strip.setPixelColor(ledShift-2, strip.Color(0,0,50));        
  }
  
  uint16_t lastLed = getLed(NUM_NOTES);
  if (!isBridgeNote(NUM_NOTES)) {
    lastLed++;
  }
  if (lastLed == LED_COUNT-2) {
    strip.setPixelColor(lastLed+1, strip.Color(0,0,50));
  }
  else if (lastLed < LED_COUNT-2) {
    strip.setPixelColor(lastLed+1, strip.Color(0,0,50));
    strip.setPixelColor(lastLed+2, strip.Color(0,0,50));
  }
  //updateNote(39, 1, strip.Color(0,50,0));
  strip.show();
}

void updateStrip(uint8_t *notes, uint32_t color) { //unsigned char*
  for (uint8_t i=0; i<NUM_NOTES/8; i++) {
    Serial.print(" ");
    Serial.print(notes[i]);
    for (uint8_t j=0; j<8; j++) {
      uint8_t note = i*8 + j + 1;
      uint8_t value = notes[i]>>(7-j) & 0x01;
      updateNote(note, value, color);
    }
  }
  strip.show();
}

void updateNote(uint8_t note, uint8_t value, uint32_t color) {
  uint16_t led = getLed(note);
  if (value == 0) {  
    color = strip.Color(0, 0, 0);
  }
  strip.setPixelColor(led, color);
  if (!isBridgeNote(note)) {                  // note=36 -> led=71 , note=72 -> led=142
    strip.setPixelColor(led + 1, color);
  }
}

uint16_t getLed(uint8_t note) {
  // -1 for note to index conversion
  // *2 for two leds/key
  // LED_SHIFT to shift LEDs in strip
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