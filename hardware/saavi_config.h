#ifndef SAVI_CONFIG_H
#define SAVI_CONFIG_H

// --- Network Credentials ---
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// --- Emergency Contact ---
const char* SOS_NUMBER = "+91XXXXXXXXXX"; // International format

// --- SĀVI System Thresholds ---
const float FALL_G_FORCE = 2.5; // Trigger for MPU6050
const int EEG_SAMPLE_RATE = 256; // Acquisition frequency in Hz

#endif