# RSA (RoadSide Alret Messages)

# This script listens for incoming US RSA (Roadside Alert Message) messages.
# It logs all received messages to a file for further analysis.

import time  # To keep the script running
import json   # To parse and process the received JSON data

# Import necessary modules from the Commsignia SDK.
from pycmssdk import (
    create_cms_api,         # Establishes a connection to the V2X system
    WsmpRxNotifData,        # Data structure for received WSMP messages
)

V2X_STACK_IP = "192.168.1.54"  # The IP address of the V2X device (OBU/RSU)
LOG_FILE = "received_us_rsa.log"  # File to save the received RSA messages

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    This function is called each time a new US RSA message is received.
    It decodes the message and logs it to a file.
    """
    try:
        # Decode the byte buffer to a JSON string and convert it to a dictionary.
        message = json.loads(buffer.decode("utf-8"))
        print("Received US RSA:", message)  # Print the received message for verification

        # Append the received message to a log file.
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")
    except Exception as e:
        print(f"Error decoding US RSA: {e}")

def receive_us_rsa():
    """
    This function subscribes to US RSA messages and continuously listens for them.

    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US RSA messages...")
        psid = 102  # PSID for US RSA messages (must match sender)
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  # Subscribe to messages with this PSID

        while True:
            time.sleep(1)  # Keep the receiver running indefinitely

if __name__ == "__main__":
    receive_us_rsa()  # Start listening for US RSA messages

'''
Normal Use of RSA 


Let's consider we are driving along a highway and approaching a construction zone. A roadside unit
(RSU) sends a RSA message to alert drivers about the road closure and potential hazards
ahead. This helps our car's navigation system warn us in time so we can safely
slow down and take an alternate route, preventing confusion and accidents.

'''