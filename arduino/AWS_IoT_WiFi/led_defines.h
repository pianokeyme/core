// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1:
#define LED_PIN 6

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 288

// How many NeoPixels are used for the keys? 84*2 + 2*2 + 2*1 = 174 LEDs
#define LED_USED_COUNT 174

// How many NeoPixels are all the used LEDs shifted by?
#define LED_SHIFT 2

// How many piano notes are there? (size of piano)
#define NUM_NOTES 88

// Colour code for sharp and flat keys. RGB: 255,87,51
#define GARNET 0x9A2A2A

// Colour code for natural keys. RGB: 128,128,128
#define GRAY   0x808080

#define RED     0xFF1744
#define YELLOW  0xFFEA00
#define GREEN   0x00E676