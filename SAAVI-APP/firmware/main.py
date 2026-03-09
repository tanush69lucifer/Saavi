import bluetooth
import random
import struct
import time
from machine import Timer

# BLE UUIDs
# You can generate custom UUIDs using `uuidgen`
SERVICE_UUID = bluetooth.UUID("19B10000-E8F2-537E-4F6C-D104768A1214")
CHAR_UUID = bluetooth.UUID("19B10001-E8F2-537E-4F6C-D104768A1214")

# Advertising payload builder
def build_advertising_payload(name=None, services=None):
    payload = bytearray()
    
    def _append(adv_type, value):
        payload.append(len(value) + 1)
        payload.append(adv_type)
        payload.extend(value)
        
    if name:
        _append(0x09, name.encode()) # Complete Local Name
    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(0x03, b) # 16-bit UUID
            elif len(b) == 16:
                _append(0x07, b) # 128-bit UUID
    return payload

class BLEServer:
    def __init__(self, name="NeuroBand"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)
        
        self.connections = set()
        self.payload = build_advertising_payload(
            name=name, 
            services=[SERVICE_UUID]
        )
        
        # Register GATT Server
        services = (
            (SERVICE_UUID, ((CHAR_UUID, bluetooth.FLAG_NOTIFY | bluetooth.FLAG_READ),)),
        )
        self.services = self.ble.gatts_register_services(services)
        self.char_handle = self.services[0][0]
        
        self._advertise()

    def _irq(self, event, data):
        if event == 1: # _IRQ_CENTRAL_CONNECT
            conn_handle, _, _ = data
            print(f"Connected: {conn_handle}")
            self.connections.add(conn_handle)
        elif event == 2: # _IRQ_CENTRAL_DISCONNECT
            conn_handle, _, _ = data
            print(f"Disconnected: {conn_handle}")
            if conn_handle in self.connections:
                self.connections.remove(conn_handle)
            self._advertise()

    def _advertise(self):
        print("Advertising...")
        self.ble.gap_advertise(100_000, adv_data=self.payload)

    def send_signal(self, value):
        """Sends a Float value over BLE as little-endian."""
        if self.connections:
            # Package float into 4 bytes
            data = struct.pack("<f", value)
            self.ble.gatts_write(self.char_handle, data)
            for conn in self.connections:
                try:
                    self.ble.gatts_notify(conn, self.char_handle, data)
                except Exception as e:
                    print("Notify failed:", e)

print("Starting Core NeuroBand BLE Firmware...")
ble_server = BLEServer("NeuroBand_ESP32")

# Timer to send data at ~2Hz (every 500ms)
def tick(timer):
    # Simulate Brainwave / Neuro Signal (Normal 0.4 to 0.6)
    simulated_val = 0.5 + (random.uniform(-0.1, 0.1))
    ble_server.send_signal(simulated_val)
    print(f"Sent: {simulated_val:.3f}")

tim = Timer(0)
tim.init(period=500, mode=Timer.PERIODIC, callback=tick)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    tim.deinit()
    ble_server.ble.active(False)
    print("Stopped.")
