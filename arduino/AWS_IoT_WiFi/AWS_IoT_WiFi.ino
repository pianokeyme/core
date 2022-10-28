/*
  AWS IoT WiFi

  This sketch securely connects to an AWS IoT using MQTT over WiFi.
  It uses a private key stored in the ATECC508A and a public
  certificate for SSL/TLS authetication.

  It publishes a message every 5 seconds to arduino/outgoing
  topic and subscribes to messages on the arduino/incoming
  topic.

  The circuit:
  - Arduino MKR WiFi 1010 or MKR1000

  The following tutorial on Arduino Project Hub can be used
  to setup your AWS account and the MKR board:

  https://create.arduino.cc/projecthub/132016/securely-connecting-an-arduino-mkr-wifi-1010-to-aws-iot-core-a9f365

  This example code is in the public domain.
*/
#include <ArduinoBearSSL.h>
#include <ArduinoECCX08.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h> // change to #include <WiFi101.h> for MKR1000

#include "arduino_secrets.h"
#include "led_defines.h"

#include <Adafruit_NeoPixel.h>

// Function Prototypes
void publishMessage();
void onMessageReceived(int messageSize);
unsigned long getTime();
void connectWiFi();
bool connectMQTT();
void colorBlink(uint32_t color, int wait);
void colorWipe(uint32_t color);
void initializeStrip();
void shiftStrip(uint8_t *notes, uint8_t direction);
void updateStrip(unsigned char* notes, uint32_t color);
void updateNote(unsigned char note, uint32_t color);
uint16_t getLed(uint8_t note);
bool isBridgeNote(uint8_t note);
void updateBridgeNotes();

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)

/////// Enter your sensitive data in arduino_secrets.h
const char ssid[]        = SECRET_SSID;
const char pass[]        = SECRET_PASS;
const char broker[]      = SECRET_BROKER;
const char* certificate  = SECRET_CERTIFICATE;

// Receiving Messages Buffer
uint8_t buf[256];
size_t bufSize = 256;

uint16_t bridgeNote1;
uint16_t bridgeNote2;
uint16_t ledShift;

WiFiClient    wifiClient;            // Used for the TCP socket connection
BearSSLClient sslClient(wifiClient); // Used for SSL/TLS connection, integrates with ECC508
MqttClient    mqttClient(sslClient);

void setup() {

  Serial.begin(115200);
  while (!Serial);

  if (!ECCX08.begin()) {
    Serial.println("No ECCX08 present!");
    while (1);
  }

  // Set a callback to get the current time
  // used to validate the servers certificate
  ArduinoBearSSL.onGetTime(getTime);

  // Set the ECCX08 slot to use for the private key
  // and the accompanying public certificate for it
  sslClient.setEccSlot(0, certificate);

  // Optional, set the client id used for MQTT,
  // each device that is connected to the broker
  // must have a unique client id. The MQTTClient will generate
  // a client id for you based on the millis() value if not set
  //
  // mqttClient.setId("clientId");

  // Set the message callback, this function is
  // called when the MQTTClient receives a message
  mqttClient.onMessage(onMessageReceived);

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(10); // Set BRIGHTNESS to about 1/5 (max = 255)
  ledShift = 2;
  updateBridgeNotes();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    colorWipe(strip.Color(100,0,0));
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    colorWipe(strip.Color(50,50,0));
    // MQTT client is disconnected, connect
    if (connectMQTT()) {
      initializeStrip();      
    }
    else {
      Serial.println();
      Serial.println("Disconnected from the WiFi network");
      return;
    }
  }

  // poll for new MQTT messages and send keep alives
  mqttClient.poll();
}
