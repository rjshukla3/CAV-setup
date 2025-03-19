# This script sends a US MAP (Map Data Message)
# US MAP messages provide detailed road layouts, lane markings, and intersection data.

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
PSID = 103  # Protocol Service Identifier (PSID) for US MAP messages

def send_us_map():
    """
    This function continuously sends Map Data Messages (MAP).
    US MAP messages help vehicles understand road geometry and intersections.
    
    """
    
    # Connect to the V2X stack using the provided IP address
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US MAP...")

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
            # Construct the message payload with road layout information
            map_payload = {
                "intersection_id": "INT_567",  # Unique intersection ID
                "road_name": "Main Street",
                "lanes": [
                    {"lane_id": 1, "lane_type": "vehicle", "direction": "north"},
                    {"lane_id": 2, "lane_type": "bike", "direction": "north"},
                    {"lane_id": 3, "lane_type": "vehicle", "direction": "south"}
                ],
                "speed_limits": {"default": 50, "lane_2": 25},  # Speed limits (km/h)
                "timestamp": int(time.time() * 1000),
            }

            # Convert the payload dictionary into a JSON-encoded byte string
            raw_message = json.dumps(map_payload).encode("utf-8")

            try:
                # Send the WSMP message over the V2X network
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US MAP: {map_payload}")  
            except Exception as e:
                print(f"[Sender] Error sending US MAP: {e}")  

            time.sleep(5)  # Send a new message every 5 seconds

if __name__ == "__main__":
    send_us_map()  # Execute the function to start sending US MAP messages


'''
General Use Case for MAP message type

For an example an autonomous vehicle is approaching an unfamiliar intersection or like 
some new constructionhas been done for which vehicle has no idea then. So, then with help
of US MAP messages, the vehicle receives lane information, traffic flow direction, and 
speed limits before entering the intersection.This ensures safe navigation and prevents
wrong turns or lane violations.

'''