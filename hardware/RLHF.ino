#define PIN_RLHF_BUTTON 14 // Physical "False Alarm" button

void setupRLHF() {
  pinMode(PIN_RLHF_BUTTON, INPUT_PULLUP);
}

void checkRLHF() {
  if (digitalRead(PIN_RLHF_BUTTON) == LOW) {
    Serial.println("RLHF: User flagged a FALSE POSITIVE.");
    // Log this timestamp to Firebase/SD Card for retraining
    delay(1000); // Debounce
  }
}