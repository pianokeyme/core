bool handle_instruction() {
  uint8_t *instr;
  instr = buf;
  if (*instr != 0x0F) {
    Serial.println("Invalid message discarded");
    return false;
  }
  instr++;
  switch (*instr) {
    case 0x64:
      Serial.println();
      Serial.println("Instr: Update Notes");
      Serial.println(*instr++);
      updateNotes(instr);
      break;
    case 0x65:
      Serial.println();
      Serial.println("Instr: Resize Piano");
      Serial.println(*instr++);
      resizePiano(instr);
      break;
    case 0x66:
      Serial.println();
      Serial.println("Instr: Change Color");
      Serial.println(*instr++);
      changeColor(instr);
      break;
    case 0x67:
      Serial.println();
      Serial.println("Instr: Change Color Scheme");
      Serial.println(*instr++);
      changeColorScheme(instr);
      break;
    default:
      break;
  }
  return true;
}

void updateNotes(uint8_t *notes) {
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

void resizePiano(uint8_t *size) {
  return;
}

void changeColor(uint8_t *color) {
  uint32_t temp_color;
  Serial.print("RGB: ");   
  for (uint8_t i=0; i<3; i++) {
    Serial.print(color[i]);
    Serial.print(" ");
    temp_color = temp_color | ((uint32_t)color[i] << ((2-i)*8));
  }
  notes_color = temp_color;
}

void changeColorScheme(uint8_t *colorscheme) {
  notes_effect = (Effects)*colorscheme;
  Serial.print("Color Scheme: ");
  Serial.print(notes_effect);
}