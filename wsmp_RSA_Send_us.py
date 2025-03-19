# RSA (Roadside Alert Message) messages.

import time # To generate timestamps for messages
import json # To format the message data as JSON

# Import necessary functions and classes from the Commsignia SDK.
from pycmssdk import (
    create_cms_api,  # Creates a connection to the V2X communication system
    WsmpSendData,  # Defines the structure of the outgoing WSMP message
    WsmpTxHdrInfo,    # Contains header details like the PSID (message type identifier)
    RadioTxParams,       # Defines radio transmission parameters such as interface, power, etc.
    MacAddr,          # Used to set the MAC address (we use broadcast in these examples)
    SecDot2TxInfo,     # Security settings for the message
    SecDot2TxSignInfo, # Signature details for secure messaging
    SignMethod,        # Specifies the signing method to use for authentication
)

V2X_STACK_IP = "192.168.1.54"  # IP address of the V2X device (like an RSU)
PSID = 102  # PSID for US RSA messages (this number is chosen based on standard definitions)

def send_us_rsa():
    """
    This function continuously sends US RSA messages.
    RSA messages warn drivers about upcoming hazards or road alerts.
    """
    # Connect to the V2X system using the provided IP address.
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US RSA messages.")

        # Define the structure of the WSMP message using transmission parameters.
        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,  # Use the first radio interface on the device
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcast address (to all nearby vehicles)
                datarate=6,     # Transmission data rate (in Mbps)
                tx_power=20,    # Transmission power (in dBm)
                expiry_time=5000,  # Message expiry time in milliseconds (5 seconds)
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=PSID),  # Set the message type to US RSA using the PSID
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,  # Use a secure signing method
                psid=PSID
            )),
        )

        while True:
            # Create the RSA payload with important alert information.
            rsa_payload = {
                "station_id": "rsu_9012",         # Unique ID of the roadside unit sending the alert
                "alert_type": "road_closure",       # Type of alert (e.g., road_closure, accident, hazardous condition)
                "description": "Road closed ahead due to maintenance work.",  # Short description of the alert
                "latitude": 52000500,               # Location of the alert (latitude in microdegrees)
                "longitude": 13000500,              # Location of the alert (longitude in microdegrees)
                "effective_time": int(time.time() * 1000),  # Time when the alert becomes effective (ms since epoch)
                "expiry_time": int(time.time() * 1000) + 300000,  # Alert expires in 5 minutes (300,000 ms)
            }

            # Convert the payload to a JSON string and then to bytes using UTF-8 encoding.
            raw_message = json.dumps(rsa_payload).encode("utf-8")

            try:
                # Send the WSMP message with the RSA payload.
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US RSA: {rsa_payload}")
            except Exception as e:
                print(f"[Sender] Error sending US RSA: {e}")

            time.sleep(5)  # Wait 5 seconds before sending the next message

if __name__ == "__main__":
    send_us_rsa()  # Start sending US RSA messages