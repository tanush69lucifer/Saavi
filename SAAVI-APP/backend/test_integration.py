import threading
import time
import requests
import json
import websocket

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/dashboard"

def test_integration():
    print("=== NeuroBand Integration Verification Script ===")
    
    # 1. Register a Patient
    patient_email = f"patient_{int(time.time())}@test.com"
    print(f"\n[1] Registering Patient: {patient_email}...")
    try:
        res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test Patient",
            "email": patient_email,
            "password": "password123",
            "role": "patient"
        })
        res.raise_for_status()
        patient_id = res.json()["id"]
        print(f"  -> Success! Patient ID: {patient_id}")
    except requests.exceptions.ConnectionError:
        print("  -> ERROR: Could not connect to the Backend. Is FastAPI running on port 8000?")
        return
    except Exception as e:
        print(f"  -> ERROR: {e} - {res.text}")
        return

    # 2. Register a Family Member
    family_email = f"family_{int(time.time())}@test.com"
    print(f"\n[2] Registering Family Member: {family_email}...")
    try:
        res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test Family",
            "email": family_email,
            "password": "password123",
            "role": "family"
        })
        res.raise_for_status()
        family_id = res.json()["id"]
        print(f"  -> Success! Family ID: {family_id}")
    except Exception as e:
        print(f"  -> ERROR: {e} - {res.text}")
        return

    # 3. Connect WebSocket for the Family Member
    print(f"\n[3] Connecting WebSocket for Family Member ID {family_id}...")
    messages_received = []

    def on_message(ws, message):
        print(f"\n  [WebSocket] Received Push Notification: {message}")
        messages_received.append(json.loads(message))

    def on_error(ws, error):
        print(f"  [WebSocket] Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("  [WebSocket] Connection Closed.")

    def on_open(ws):
        print("  [WebSocket] Connected successfully!")

    # Start WebSocket in a separate thread so it doesn't block out HTTP requests
    ws_client = websocket.WebSocketApp(
        f"{WS_URL}/{family_id}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws_thread = threading.Thread(target=ws_client.run_forever, daemon=True)
    ws_thread.start()

    # Wait a brief moment to ensure connection opens
    time.sleep(1)

    # 4. Patient Uploads Normal Signal
    print(f"\n[4] Uploading a NORMAL signal from Patient ID {patient_id}...")
    try:
        res = requests.post(f"{BASE_URL}/api/signals", json={
            "value": 0.55,
            "status": "normal",
            "patient_id": patient_id
        })
        res.raise_for_status()
        print("  -> Success! Normal signal saved in Database.")
    except Exception as e:
        print(f"  -> ERROR: {e} - {res.text}")

    # Wait a bit to ensure no WS message is falsely triggered
    time.sleep(1)
    if len(messages_received) == 0:
        print("  -> Passed Verification: No WebSocket message broadcasted for normal signal.")
    else:
        print("  -> FAILED: Received unexpected WebSocket broadcast for a normal signal!")

    # 5. Patient Uploads Anomalous Signal
    print(f"\n[5] Uploading an ANOMALOUS signal from Patient ID {patient_id}...")
    try:
        res = requests.post(f"{BASE_URL}/api/signals", json={
            "value": 0.82,
            "status": "anomalous",
            "patient_id": patient_id
        })
        res.raise_for_status()
        print("  -> Success! Anomalous signal saved in Database.")
    except Exception as e:
        print(f"  -> ERROR: {e} - {res.text}")

    # Wait for the WebSocket push notification
    time.sleep(1)
    if len(messages_received) > 0 and messages_received[-1]["type"] == "anomaly_alert":
        print("  -> Passed Verification: WebSocket anomaly alert instantly pushed & received by Family Member!")
    else:
        print("  -> FAILED: Did not receive the expected WebSocket broadcast anomaly alert.")

    print("\n=== Verification Script Complete ===")
    
    # Close socket properly
    ws_client.close()
    ws_thread.join(timeout=2)


if __name__ == "__main__":
    test_integration()
