# This script sends a US BSM (Basic Safety Message)
# US BSM messages share vehicle status (position, speed, heading) with other vehicles.
"""
    This function continuously sends Basic Safety Messages (BSM).
    BSM messages help vehicles share their location, speed, and heading for safety.
    Basically talking for line 25 here.
"""
import time  # Used to generate timestamps for messages
import json  # Used to format the message data as JSON

# Import necessary modules from the Commsignia SDK
from pycmssdk import (
    create_cms_api,  # Creates a connection to the V2X stack
    WsmpSendData,  # Defines the message format for WSMP communication
    WsmpTxHdrInfo,  # Contains WSMP header information
    RadioTxParams,  # Defines the radio transmission parameters
    MacAddr,  # Used to define the MAC address for broadcasting
    SecDot2TxInfo,  # Security settings for the message
    SecDot2TxSignInfo,  # Signature information to ensure secure transmission
    SignMethod,  # Specifies the signing method for authentication
)

V2X_STACK_IP = "192.168.1.54"  # The IP address of the V2X device (OBU/RSU)
PSID = 100  # Protocol Service Identifier (PSID) for US BSM messages

def send_us_bsm():
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US BSM...")

        # Define WSMP transmission parameters
        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,  # Identifies which radio interface to use (default: 1)
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcasts to all vehicles in range
                datarate=6,  # Data rate for message transmission
                tx_power=20,  # Transmission power level
                expiry_time=1000,  # The message expires after 1 second
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=PSID),  # Assigning PSID specific to BSM messages
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,  # Uses a signing method for security
                psid=PSID  # Ensures the message is only processed by devices subscribed to this PSID
            )),
        )

        while True:
            # Basically constructing the message payload with vehicle status
            bsm_payload = {
                "station_id": "vehicle_1234",  # Unique ID for the sending vehicle
                "vehicle_type": "car",  # Type of vehicle (can be bus, bike, truck, etc.)
                "latitude": 52000000,  # Vehicle's current latitude (microdegrees)
                "longitude": 13000000,  # Vehicle's current longitude (microdegrees)
                "speed": 15000,  # Speed in millimeters per second (15 m/s)
                "heading": 9000,  # Direction the car is moving in (0.01 degrees)
                "timestamp": int(time.time() * 1000),  # Time the message was created
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(bsm_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US BSM: {bsm_payload}")  # Print the sent message for verification
            except Exception as e:
                print(f"[Sender] Error sending US BSM: {e}")  # Print any error messages

            time.sleep(1)  # Send a new message every 1 second

if __name__ == "__main__":
    send_us_bsm()  # Execute the function to start sending US BSM messages


'''
This is basically a general example for BSM (use case of BSM)

Imagine we're driving in dense fog on the highway/wide road &
we cannot able to see the car ahead of us, but with use of BSM messages, 
our car's system receives live updates from vehicles nearby. 
If a car ahead suddenly brakes, our system warns you before you even see it,
preventing collisions.

'''