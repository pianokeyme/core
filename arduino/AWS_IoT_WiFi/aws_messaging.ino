void publishMessage() {
  Serial.println("Publishing message");

  // send message, the Print interface can be used to set the message contents
  mqttClient.beginMessage("arduino/outgoing");
  mqttClient.print("hello ");
  mqttClient.print(millis());
  mqttClient.endMessage();
}

void onMessageReceived(int messageSize) {
  //Serial.print(getTime());
  // we received a message, print out the topic and contents
  Serial.print("Received a message with topic '");
  Serial.print(mqttClient.messageTopic());
  Serial.print("', length ");
  Serial.print(messageSize);
  Serial.println(" bytes:");

  // use the Stream interface to print the contents
  if (mqttClient.available()) {
    Serial.print(mqttClient.read(buf, bufSize));
    Serial.print(messageSize);
  }
  Serial.println();

  uint8_t *instr;
  instr = buf;
  if (*instr != 0x0F) {
    Serial.print("Invalid message discarded");
    return;
  }
  instr++;
  switch (*instr) {
    case 0x64:
      Serial.println("");
      Serial.println("Instr: Update Strip");
      Serial.print(*instr);
      updateStrip(++instr);
      break;
    default:
      break;
  }

  Serial.println();
}