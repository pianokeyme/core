void colorWipe(uint32_t color) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
  }
  strip.show();    //  Update strip to match
}

void updateStrip(unsigned char* notes) {
  unsigned char *t;
  for (t=notes; *t!='\0'; t++) {
    updateNote(*t);
  }
  strip.show();
}

void updateNote(unsigned char note) {
  // -1 for note to index conversion
  // *2 for two leds/key
  // LED_SHIFT to shift LEDs in strip
  // floor(note/(36-((LED_SHIFT-2)*2))) to count number of 1 leds/key notes that came before this one, taking LED_SHIFT into account
  int led = ((note-1) * 2) + LED_SHIFT - floor(note/(36-((LED_SHIFT-2)*2)));
  if (note == 36 || note == 72) {                  // note=36 -> led=71 , note=72 -> led=142
    strip.setPixelColor(led, strip.Color(255, 87, 51));
  }
  else {
    strip.setPixelColor(led, strip.Color(255, 87, 51));
    strip.setPixelColor(led + 1, strip.Color(255, 87, 51));
  }
}