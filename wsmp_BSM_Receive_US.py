# This script listens for incoming US BSM (Basic Safety Messages)
# It logs all received messages to a file.

import time  # Used to keep the receiver running
import json  # Used to parse received message data

# Import necessary modules from the Commsignia SDK
from pycmssdk import (
    create_cms_api,  # Establish a connection to the V2X stack
    WsmpRxNotifData,  # Defines the structure of received WSMP messages
)

V2X_STACK_IP = "192.168.1.54"  # The IP address of the V2X device (OBU/RSU)
LOG_FILE = "received_us_bsm.log"  # File where received BSM messages will be logged

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    This Callback function basically processes received BSM messages.
    This function work whenever a new message is received.
    """
    try:
        # Convert the received byte buffer into a JSON dictionary
        message = json.loads(buffer.decode("utf-8"))
        
        print("Received US BSM:", message)  # Print received message to console
        
        # Save the received message to a log file for later analysis
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")  # Write each message on a new line
            
    except Exception as e:
        print(f"Error decoding US BSM: {e}")  # Print any errors that occur

def receive_us_bsm():
    """
    This function subscribes to US BSM messages and listens for them continuously.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US BSM messages...")

        psid = 100  # PSID for US BSM messages (same as sender)
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  # Subscribe to US BSM messages

        while True:
            time.sleep(1)  # Keeps the script running indefinitely

if __name__ == "__main__":
    receive_us_bsm()  # Execute the function to start listening for US BSM messages


'''
This is basically a general example for BSM (use case of BSM)

For an example just have a scenario that: We're driving on foggy day on the highway/wide road &
we cannot able to see the car ahead of us, but with use of BSM messages, 
our car's system receives live updates from vehicles nearby. 
If a car ahead suddenly brakes, our system warns you before you even see it,
preventing collisions.

'''