#define PIN_HAPTIC 12 // GPIO for LRA Motor
#define PIN_BUZZER 13 // GPIO for 5V Buzzer

void setupFeedback() {
  pinMode(PIN_HAPTIC, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
}

// Discreet "Pre-Alert" vibration
void playVibration() {
  for(int i=0; i<3; i++) {
    digitalWrite(PIN_HAPTIC, HIGH);
    delay(200);
    digitalWrite(PIN_HAPTIC, LOW);
    delay(100);
  }
}

// Loud "Tier 3" Emergency Alarm
void playLoudAlarm() {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(5000); 
  digitalWrite(PIN_BUZZER, LOW);
}