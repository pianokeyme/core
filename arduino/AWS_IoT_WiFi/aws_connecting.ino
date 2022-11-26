unsigned long getTime() {
  // get the current time from the WiFi module  
  return WiFi.getTime();
}

void connectWiFi() {
  Serial.print("Attempting to connect to SSID: ");
  Serial.println(wificreds.ssid);

  const char* s = wificreds.ssid.c_str();
  const char* p = wificreds.pass.c_str();

  for (uint8_t i=0; i<5; i++) {
    if(WiFi.begin(s, p) == WL_CONNECTED) {
      Serial.println();
      Serial.println("You're connected to the network!");
      Serial.println();
      return;
    }
    // failed, retry
    Serial.print(".");
    colorBlink(RED, 100);
    delay(5000);
  }

  Serial.println();
  Serial.println("Failed to connect to the network");
  Serial.println();
}

bool connectMQTT() {
  Serial.print("Attempting to MQTT broker: ");
  Serial.print(broker);
  Serial.println();

  while (!mqttClient.connect(broker, 8883)) {
    // failed, retry
    if (WiFi.status() != WL_CONNECTED) {
      return false;
    }
    Serial.print(".");
    colorBlink(YELLOW, 100);
    delay(5000);
  }
  Serial.println();
  Serial.println("You're connected to the MQTT broker");
  Serial.println();

  // subscribe to a topic
  mqttClient.subscribe("arduino/incoming");

  return true;
}