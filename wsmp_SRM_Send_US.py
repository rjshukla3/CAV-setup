# SRM (Signal Request Messages)

# This script sends a US SRM (Signal Request Message)
# US SRM messages are sent by emergency vehicles or buses to request priority at traffic lights.

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
PSID = 105  # Protocol Service Identifier (PSID) for US SRM messages

def send_us_srm():
    """
    This function continuously sends Signal Request Messages (SRM).
    US SRM messages help emergency and transit vehicles request green lights.
    """
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US SRM...")

        # Define WSMP transmission parameters
        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,  
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcast to all vehicles
                datarate=6,  
                tx_power=20,  
                expiry_time=5000,  
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=PSID),  
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,  
                psid=PSID  
            )),
        )

        while True:
            # Construct the message payload with signal request information
            srm_payload = {
                "vehicle_id": "firetruck_1",  # ID of the requesting vehicle
                "vehicle_type": "emergency",  # Emergency, bus, or transit vehicle
                "intersection_id": 321,  # Intersection where request is made
                "requested_phase": "green",  # Requested light change
                "priority_level": "high",  # Level of priority (emergency = high)
                "timestamp": int(time.time() * 1000),
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(srm_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US SRM: {srm_payload}")  
            except Exception as e:
                print(f"[Sender] Error sending US SRM: {e}")  

            time.sleep(5)  # Send a new message every 5 seconds

if __name__ == "__main__":
    send_us_srm()  # Execute the function to start sending US SRM messages

'''
I know complicated example but easy way to expalin use case of SRM

Imagine a firetruck is rushing to an emergency. Normally, it must wait at red lights, delaying
its response but with US SRM messages, the firetruck requests for priority at intersections,
turning the light green before arrival, ensuring faster and safer emergency response.

'''