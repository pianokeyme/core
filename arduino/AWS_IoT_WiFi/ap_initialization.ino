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

void listenForClients() {
  WiFiClient client;
  bool ssid_acquired = false;
  bool pass_acquired = false;
  while (!client) {
    checkStatus();
    client = server.available();   // listen for incoming clients

    if (client) {                             // if you get a client,
      Serial.println("new client");           // print a message out the serial port
      String currentLine = "";                // make a String to hold incoming data from the client
      while (client.connected()) {            // loop while the client's connected
        delayMicroseconds(10);                // This is required for the Arduino Nano RP2040 Connect - otherwise it will loop so fast that SPI will never be served.
        if (client.available()) {             // if there's bytes to read from the client,
          char c = client.read();             // read a byte, then
          Serial.write(c);                    // print it out the serial monitor
          if (c == '\n') {                    // if the byte is a newline character

            // if the current line is blank, you got two newline characters in a row.
            // that's the end of the client HTTP request, so send a response:
            if (currentLine.length() == 0) {
              // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
              // and a content-type so the client knows what's coming, then a blank line:
              client.println("HTTP/1.1 200 OK");
              client.println("Content-type:text/html");
              client.println();

              // the content of the HTTP response follows the header:
              // client.print("Click <a href=\"/H\">here</a> turn the LED on<br>");
              // client.print("Click <a href=\"/L\">here</a> turn the LED off<br>");

              client.print("<a href=\"/TEXT_SSID\">Submit SSID</a><br><br>"); // Replace TEXT with SSID to test
              client.print("<a href=\"/TEXT_PASS\">Submit PASS</a><br><br>"); // REPLACE TEXT with PASS to test

              // The HTTP response ends with another blank line:
              client.println();
              // break out of the while loop:
              break;
            }
            else {      // if you got a newline, then clear currentLine:
              currentLine = "";
            }
          }
          else if (c != '\r') {    // if you got anything else but a carriage return character,
            currentLine += c;      // add it to the end of the currentLine
          }

          // Check to see if the client request was "GET /H" or "GET /L":
          if (currentLine.startsWith("GET /") && currentLine.endsWith("_SSID")) {
            ssid = currentLine.substring(5, currentLine.length()-5);
            Serial.println();
            Serial.print("***Acquired Client SSID:: ");
            Serial.println(ssid);
            ssid_acquired = true;
          }
          if (currentLine.startsWith("GET /") && currentLine.endsWith("_PASS")) {
            pass = currentLine.substring(5, currentLine.length()-5);
            Serial.println();
            Serial.print("***Acquired Client PASS:: ");
            Serial.println(pass);
            pass_acquired = true;
          }
          if (ssid_acquired && pass_acquired) {
            Serial.println();
            Serial.println("***** Both Client SSID and PASS Acquired *****");
            Serial.println();
            return;
          }
        }
      }
      // close the connection:
      client.stop();
      Serial.println("client disconnected");
    }
  }
}