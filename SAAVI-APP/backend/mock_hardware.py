import time
import requests
import random

BASE_URL = "http://10.59.209.203:8000"
PATIENT_ID = 7 # Seeded Patient ID

def mock_hardware():
    print("=== NeuroBand Mock Hardware Simulator ===")
    print(f"Targeting Patient ID: {PATIENT_ID}")
    print("Press CTRL+C to stop.\n")
    
    count = 0
    try:
        while True:
            count += 1
            # Randomly trigger an anomaly every 10 samples
            is_anomaly = count % 10 == 0
            
            value = 0.5 + random.uniform(-0.1, 0.1)
            status = "normal"
            
            if is_anomaly:
                value = 0.85 + random.uniform(0, 0.1)
                status = "anomalous"
                print(f"[!] TRIGGERING ANOMALY: {value:.3f}")
            else:
                print(f"Sending normal signal: {value:.3f}")

            try:
                res = requests.post(f"{BASE_URL}/api/signals", json={
                    "value": value,
                    "status": status,
                    "patient_id": PATIENT_ID
                })
                if res.status_code == 200:
                    if is_anomaly:
                        print("  -> Sync Success: Alert broadcasted to WebSockets!")
                else:
                    print(f"  -> Error: {res.status_code} - {res.text}")
            except Exception as e:
                print(f"  -> Connection Error: {e}")

            # Send data every 2 seconds
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    mock_hardware()
