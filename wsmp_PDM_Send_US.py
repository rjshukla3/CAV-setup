# Probe Data Message (PDM).

# PDM messages carry probe data from a vehicle, such as detailed sensor information.
# This helps in collecting real-time data about road conditions.

import time   # For timestamps
import json   # For converting data to JSON

from pycmssdk import (
    create_cms_api,   # Connects to the V2X stack
    WsmpSendData,    # Defines the structure for sending WSMP messages
    WsmpTxHdrInfo,   # Contains header information (like PSID)
    RadioTxParams,   # Defines radio settings (interface, power, etc.)
    MacAddr,       # To set the destination MAC address (here: broadcast)
    SecDot2TxInfo,     # Security configuration for messages
    SecDot2TxSignInfo,  # Signature information for secure messaging
    SignMethod,    # Method used for signing messages
)

V2X_STACK_IP = "192.168.1.54"  # V2X device IP address (RSU/OBU)
PSID = 109     # PSID for US PDM messages

def send_us_pdm():
    """
    This function sends US Probe Data Messages continuously.
    These messages carry detailed sensor data from the vehicle.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US PDM...")

        # Set up the WSMP message structure
        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,  # Use radio interface 1
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcast address
                datarate=6, # Data rate in Mbps
                tx_power=20,  # Transmission power in dBm
                expiry_time=1000,# Message expires after 1 second
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=PSID),  # Set PSID to 109 for PDM
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,  # Use certificate-based signing
                psid=PSID
            )),
        )

        while True:
            # Build a sample probe data payload.
            pdm_payload = {
                "station_id": "vehicle_5678",  # Unique vehicle ID
                "temperature": 35.2,    # Example sensor data (°C)
                "humidity": 70,   # Example sensor data (%)
                "road_condition": "wet", # Road surface condition
                "timestamp": int(time.time() * 1000),  # Current time in ms
            }
            # Convert the dictionary into a JSON string then to bytes.
            raw_message = json.dumps(pdm_payload).encode("utf-8")

            try:
                # Send the PDM message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US PDM: {pdm_payload}")
            except Exception as e:
                print(f"[Sender] Error sending US PDM: {e}")

            time.sleep(1)

if __name__ == "__main__":
    send_us_pdm()

'''
Most Common Use of PDM


So it is advanced fleet management system which help in collects real-time sensor data
from each vehicle (like temperature and road conditions) using US PDM messages.
This helps a transport company monitor vehicle health and road conditions 
for better maintenance planning.

'''