void listenForClients() {
  WiFiClient client;
  while (!client) {
    checkStatus();
    client = server.available();   // listen for incoming clients
    if (client) {                             // if you get a client,
      Serial.print("new client");           // print a message out the serial port
      String currentLine = "";                // make a String to hold incoming data from the client
      while (client.connected()) {            // loop while the client's connected
        delayMicroseconds(10);                // This is required for the Arduino Nano RP2040 Connect - otherwise it will loop so fast that SPI will never be served.
        if (client.available()) {             // if there's bytes to read from the client,
          char c = client.read();             // read a byte, then
          Serial.write(c);                    // print it out the serial monitor
          // That's the end of the client HTTP request, so send a response:
          if (c == '#') {
            client.println("HTTP/1.1 200 OK");
            client.println();            
            // break out of the while loop:
            break;
          }
          else if (c == '\n') {      // if you got a newline, then clear currentLine:
            if (currentLine.indexOf("wifi_ssid") >= 0) {
              wificreds.ssid = currentLine.substring(10);
            }
            else if (currentLine.indexOf("wifi_pass") >= 0) {
              wificreds.pass = currentLine.substring(10);
            }
            currentLine = "";
          }
          else if (c != '\r') {    // if you got anything else but a carriage return character,
            currentLine += c;      // add it to the end of the currentLine
          }
        }
      }
      // close the connection:
      client.stop();
      Serial.println();
      Serial.println("client disconnected");
      Serial.println();
      Serial.print("***Acquired Client SSID:: ");
      Serial.println(wificreds.ssid);
      Serial.print("***Acquired Client PASS:: ");
      Serial.println(wificreds.pass);
      Serial.println();
      return;
    }
  }
}