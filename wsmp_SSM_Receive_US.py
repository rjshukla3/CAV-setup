'''
SSM (Signal Status Messages)

SSM messages basically provide feedback on signal priority requests made by emergency
vehicles or public transit using SRM Messages.This allows vehicles to confirm if their
priority request was granted or denied at an intersection.

'''


# This script listens for incoming US SSM (Signal Status Messages)
# It logs all received messages to a file.

import time  # Used to keep the receiver running
import json  # Used to parse received message data

# Import necessary modules from the Commsignia SDK
from pycmssdk import (
    create_cms_api,  # Establish a connection to the V2X stack
    WsmpRxNotifData,  # Defines the structure of received WSMP messages
)

V2X_STACK_IP = "192.168.1.54"  # The IP address of the V2X device (OBU/RSU)
LOG_FILE = "received_us_ssm.log"  # File where received SSM messages will be logged

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    Callback function that processes received US SSM messages.
    This function gets triggered whenever a new message is received.
    """
    try:
        # Convert the received byte buffer into a JSON dictionary
        message = json.loads(buffer.decode("utf-8"))
        
        print("Received US SSM:", message)  # Print received message to console
        
        # Save the message to a log file for later analysis
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")  
            
    except Exception as e:
        print(f"Error decoding US SSM: {e}")  

def receive_us_ssm():
    """
    This function subscribes to US SSM messages and listens for them continuously.
    
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US SSM messages...")

        psid = 106  # PSID for US SSM messages (same as sender)
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  

        while True:
            time.sleep(1)  

if __name__ == "__main__":
    receive_us_ssm()  # Execute the function to start listening for US SSM messages
