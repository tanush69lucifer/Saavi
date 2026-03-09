
#include "savi_config.h"      // Load WiFi and SOS Number
#include "savi_model_data.h"  // Load AI Weights#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <HardwareSerial.h>

// --- HARDWARE CONFIGURATION ---
#define EXG_PILL_PIN 1      // Analog input from ExG Pill (ADC1_CH0)
#define MODEM_RX 16         // ESP32-S3 RX2
#define MODEM_TX 17         // ESP32-S3 TX2
#define I2C_SDA 4           //
#define I2C_SCL 5           //
#define SOS_NUMBER "+91XXXXXXXXXX" // Replace with Emergency Contact

// --- SENSING PARAMETERS ---
const float FALL_LIMIT = 2.5; // G-force threshold for falls
const int SAMPLE_RATE = 256;  // Hz for EEG acquisition

Adafruit_MPU6050 mpu;
HardwareSerial SIM800L(2);

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);
  SIM800L.begin(9600, SERIAL_8N1, MODEM_RX, MODEM_TX);

  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("MPU6050 Error!");
    while (1) yield();
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  
  // Initialize SIM800L
  delay(3000); 
  SIM800L.println("AT"); 
  delay(500);
  SIM800L.println("AT+CMGF=1"); // SMS Text Mode
  
  Serial.println("SĀVI SYSTEM INITIALIZED");
}

void loop() {
  static unsigned long lastSample = 0;
  
  // 1. High-Frequency EEG Sampling
  if (micros() - lastSample >= (1000000 / SAMPLE_RATE)) {
    lastSample = micros();
    int eegRaw = analogRead(EXG_PILL_PIN);
    // Here: Push eegRaw to your 1D-CNN Buffer
  }

  // 2. Motion & Fall Logic
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  float totalAccel = sqrt(sq(a.acceleration.x) + sq(a.acceleration.y) + sq(a.acceleration.z));

  if (totalAccel > (FALL_LIMIT * 9.8)) {
    triggerEmergency("SĀVI ALERT: Sudden impact/fall detected.");
  }

  // 3. Serial Debug for Waveform
  Serial.printf("EEG:%d,Accel:%.2f\n", analogRead(EXG_PILL_PIN), totalAccel);
}

void triggerEmergency(String alertMsg) {
  Serial.println("EMERGENCY TRIGGERED");
  SIM800L.print("AT+CMGS=\"");
  SIM800L.print(SOS_NUMBER);
  SIM800L.println("\"");
  delay(1000);
  SIM800L.print(alertMsg);
  delay(100);
  SIM800L.write(26); // Send SMS
  delay(5000); // Debounce
}