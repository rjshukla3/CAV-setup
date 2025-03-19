# SSM (Signal Status Message)

# This script sends a US SSM (Signal Status Message)
# US SSM messages provide confirmation of traffic signal priority requests.

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
PSID = 106  # Protocol Service Identifier (PSID) for US SSM messages

def send_us_ssm():
    """
    This function continuously sends Signal Status Messages (SSM).
    US SSM messages inform vehicles if their traffic light priority request was approved or denied.
    
    """
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US SSM...")

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
            # Construct the message payload with signal status confirmation
            ssm_payload = {
                "intersection_id": 321,  # Unique ID of the intersection
                "requesting_vehicle_id": "firetruck_1",  # The vehicle that made the request
                "status": "granted",  # Status of request (granted, pending, denied)
                "priority_level": "high",  # Level of priority
                "timestamp": int(time.time() * 1000),
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(ssm_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US SSM: {ssm_payload}")  
            except Exception as e:
                print(f"[Sender] Error sending US SSM: {e}")  

            time.sleep(5)  # Send a new message every 5 seconds

if __name__ == "__main__":
    send_us_ssm()  # Execute the function to start sending US SSM messages

'''
Common use of SSM type message subscription

Considering an ambulance/Firebrigade requests a green light at an intersection using an SRM message.
However, without confirmation, the driver doesn't know if the request was approved or not,
but with help of US SSM messages, the ambulance/firebrigade will receives feedback,
confirming whether the priority was granted or denied.

'''