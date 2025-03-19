# SPAT (Signal Phase and Timing Message)

# This script sends a US SPAT (Signal Phase and Timing Message)
# US SPAT messages provide real-time traffic light status and timing.

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
PSID = 104  # Protocol Service Identifier (PSID) for US SPAT messages

def send_us_spat():
    """
    This function continuously sends Signal Phase and Timing (SPAT) messages.
    US SPAT messages help vehicles predict traffic light changes at intersections.
    
    """
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US SPAT...")

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
            # Construct the message payload with traffic light information
            spat_payload = {
                "intersection_id": 321,  # Unique ID of the intersection
                "signal_group": 5,  # Traffic signal group
                "current_phase": "green",  # Current traffic light color
                "remaining_time": 30,  # Seconds until light change
                "timestamp": int(time.time() * 1000),
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(spat_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US SPAT: {spat_payload}")  
            except Exception as e:
                print(f"[Sender] Error sending US SPAT: {e}")  

            time.sleep(5)  # Send a new message every 5 seconds

if __name__ == "__main__":
    send_us_spat()  # Execute the function to start sending US SPAT messages


'''
Basic Use case of SPAT(Signal Phase and Timing Messages)


Like for an example we're approaching a traffic light, but not sure if it's about to change.
Normally, we'd slow down just in that case, which wastes fuel as well increases in traffic
congestion, with help of US SPAT messages, our car will receives real-time traffic light
data and adjusts speed to pass smoothly through a green light, avoiding unnecessary braking.

'''