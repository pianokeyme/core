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
      Serial.print(*instr++);
      Serial.println(" Instr: Update Notes");
      updateNotes(instr);
      Serial.println();
      break;
    case 0x65:
      Serial.print(*instr++);
      Serial.println(" Instr: Resize Piano");
      resizePiano(instr);
      Serial.println();
      break;
    case 0x66:
      Serial.print(*instr++);
      Serial.println(" Instr: Change Color");
      changeColor(instr);
      Serial.println();
      break;
    case 0x67:
      Serial.print(*instr++);
      Serial.println(" Instr: Change Color Scheme");
      changeColorScheme(instr);
      Serial.println();
      break;
    default:
      break;
  }
  return true;
}

void updateNotes(uint8_t *notes) {
  for (uint8_t i=0; i<NUM_NOTES/8; i++) {
    Serial.print(notes[i]);
    Serial.print(" ");
    for (uint8_t j=0; j<8; j++) {
      uint8_t note = i*8 + j + 1;
      uint8_t value = notes[i]>>(7-j) & 0x01;
      updateNote(note, value);
    }
  }
  strip.show();
  Serial.println();
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
  Serial.println();
}

void changeColorScheme(uint8_t *colorscheme) {
  notes_effect = (Effects)*colorscheme;
  Serial.print("Color Scheme: ");
  Serial.println(notes_effect);
}