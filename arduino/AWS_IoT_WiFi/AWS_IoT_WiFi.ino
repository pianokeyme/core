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
#include <WiFiNINA.h>

#include "arduino_secrets.h"
#include "led_defines.h"

#include <Adafruit_NeoPixel.h>

// Function Prototypes
void printWiFiStatus();
void checkStatus();
void createAccessPoint();
void listenForClients();
unsigned long getTime();
void connectWiFi();
bool connectMQTT();
void publishMessage();
void onMessageReceived(int messageSize);
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
String ssid;
String pass;
const char broker[]      = SECRET_BROKER;
const char* certificate  = SECRET_CERTIFICATE;

const char ap_ssid[]     = SECRET_AP_SSID; // your network SSID (name)
const char ap_pass[]     = SECRET_AP_PASS; // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;
WiFiServer server(80);

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
  
  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (1);
  }
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
  // Set the message callback, this function is
  // called when the MQTTClient receives a message
  mqttClient.onMessage(onMessageReceived);

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(10); // Set BRIGHTNESS to about 1/5 (max = 255)
  ledShift = 2;
  updateBridgeNotes();
}

/*
1. If not connected to wifi, turn AP on
2, Listen for connection.
3. Once connected, wait for message.
4. Once message received, test it with connect wifi
   If doesn't work, say doesn't work and go back to 3.
5. If works, turn AP off and proceed
*/

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    colorWipe(strip.Color(100,0,0));
    while (WiFi.status() != WL_CONNECTED) {
      createAccessPoint();
      listenForClients();
      connectWiFi();
    }
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
