void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
}

void checkStatus() {
  if (status != WiFi.status()) {
    status = WiFi.status();
    switch (status) {
      case WL_IDLE_STATUS:
        Serial.println("AP disabled");
        break;
      case WL_AP_LISTENING:
        Serial.println("Listening for AP connections");
        break;
      case WL_AP_CONNECTED:
        Serial.println("Device connected to AP");
        break;
      default:
        Serial.print("KeyMe Error: ");
        Serial.println(status);
        break;
    }
  }
}

void createAccessPoint() {
  // by default the local IP address will be 192.168.4.1
  // you can override it with the following:
  // WiFi.config(IPAddress(10, 0, 0, 1));

  // print the network name (SSID);
  Serial.print("Creating access point named: ");
  Serial.println(ap_ssid);

  // Create open network. Change this line if you want to create an WEP network:
  status = WiFi.beginAP(ap_ssid, ap_pass);
  if (status != WL_AP_LISTENING) {
    Serial.println("Creating access point failed");
    while (1);
  }
  // wait 10 seconds for connection:
  delay(10000);
  // start the web server on port 80
  server.begin();
  // you're connected now, so print out the status
  printWiFiStatus();
}
