# This script sends a US TIM (Traveler Information Message)
# US TIM messages provide important road updates such as construction alerts and detours.

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
PSID = 101  # Protocol Service Identifier (PSID) for US TIM messages

def send_us_tim():
    """
    This function continuously sends Traveler Information Messages (TIM).
    US TIM messages inform drivers about road conditions, construction zones, and detours.

    """
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US TIM...")

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
            # Construct the message payload with road alert information
            tim_payload = {
                "message_id": "TIM_789",  # Unique message ID
                "event_type": "construction",  # Type of event
                "location": {"latitude": 52001234, "longitude": 13004567},
                "description": "Roadwork ahead, expect delays.",
                "start_time": int(time.time() * 1000),  # Time message was created
                "end_time": int(time.time() * 1000) + 3600000,  # Message expires in 1 hour
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(tim_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US TIM: {tim_payload}")  
            except Exception as e:
                print(f"[Sender] Error sending US TIM: {e}")  

            time.sleep(10)  # Send a new message every 10 seconds

if __name__ == "__main__":
    send_us_tim()  # Execute the function to start sending US TIM messages

'''
Basic Example for a idea of TIM (Traveler Information Message)

Imagine we're driving on a highway, and roadwork is going ahead. Normally, we only got to
find out when we see the construction signs, which might be too late to take an alternate
route but with the help of US TIM messages, our vehicle will receives an alert about
construction ahead and allowing us to reroute early and avoid delays or any kind of mishappen.

'''