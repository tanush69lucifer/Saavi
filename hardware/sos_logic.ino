#include <HardwareSerial.h>

// Professional SIM800L SOS Script
void triggerSOS(String message) {
  Serial.println("SĀVI: Initiating Emergency Protocol...");
  
  // 1. Check Signal Strength
  SIM800L.println("AT+CSQ"); 
  delay(500);
  
  // 2. Set to Text Mode
  SIM800L.println("AT+CMGF=1"); 
  delay(500);
  
  // 3. Send SMS
  SIM800L.print("AT+CMGS=\"");
  SIM800L.print(SOS_NUMBER); // Defined in Main S3 code
  SIM800L.println("\"");
  delay(1000);
  
  SIM800L.print(message);
  delay(100);
  
  // 4. Finalize with CTRL+Z
  SIM800L.write(26); 
  Serial.println("SĀVI: SOS Dispatched.");
  delay(5000); // Cooldown
}