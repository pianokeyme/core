void colorBlink(uint32_t color, int wait) {
  for (int i=0; i<3; i++) {
    delay(wait);
    colorWipe(color);
    delay(wait);
    colorWipe(strip.Color(0,0,0));
  }
}

void colorWipe(uint32_t color) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
  }
  strip.show();    //  Update strip to match
}

void updateStrip(uint8_t *notes) { //unsigned char*
  for (uint8_t i=0; i<NUM_NOTES/8; i++) {
    Serial.print(" ");
    Serial.print(notes[i]);
    for (uint8_t j=0; j<8; j++) {
      uint8_t note = i*8 + j + 1;
      uint8_t value = notes[i]>>(7-j) & 0x01;
      updateNote(note, value);
    }
  }
  strip.show();
}

void updateNote(uint8_t note, uint8_t value) {
  // -1 for note to index conversion
  // *2 for two leds/key
  // LED_SHIFT to shift LEDs in strip
  // floor(note/(36-((LED_SHIFT-2)*2))) to count number of 1 leds/key notes that came before this one, taking LED_SHIFT into account
  uint16_t led = ((note-1) * 2) + LED_SHIFT;
  if (note > bridgeNote1) {
    led = --led;
  }
  if (note > bridgeNote2) {
    led = --led;
  }

  if (value == 0x01) {  
    strip.setPixelColor(led, strip.Color(255, 87, 51));
    if (note != bridgeNote1 && note != bridgeNote2) {                  // note=36 -> led=71 , note=72 -> led=142
      strip.setPixelColor(led + 1, strip.Color(255, 87, 51));
    }
  }    
  else {
    strip.setPixelColor(led, strip.Color(0, 0, 0));
    if (note != bridgeNote1 && note != bridgeNote2) {
      strip.setPixelColor(led + 1, strip.Color(0, 0, 0));
    }
  }
}