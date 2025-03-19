# TIM(Traveler Information Messages)

# This script listens for incoming US TIM (Traveler Information Messages)
# It logs all received messages to a file.

import time  # Used to keep the receiver running
import json  # Used to parse received message data

# Import necessary modules from the Commsignia SDK
from pycmssdk import (
    create_cms_api,  # Establish a connection to the V2X stack
    WsmpRxNotifData,  # Defines the structure of received WSMP messages
)

V2X_STACK_IP = "192.168.1.54"  # The IP address of the V2X device (OBU/RSU)
LOG_FILE = "received_us_tim.log"  # File where received TIM messages will be logged

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    Callback function that processes received US TIM messages.
    This function gets triggered whenever a new message is received.
    """
    try:
        # Convert the received byte buffer into a JSON dictionary
        message = json.loads(buffer.decode("utf-8"))
        
        print("Received US TIM:", message)  # Print received message to console
        
        # Save the received message to a log file for later analysis
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")  
            
    except Exception as e:
        print(f"Error decoding US TIM: {e}")  

def receive_us_tim():
    """
    This function subscribes to US TIM messages and listens for them continuously.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US TIM messages...")

        psid = 101  # PSID for US TIM messages (same as sender)
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  

        while True:
            time.sleep(1)  

if __name__ == "__main__":
    receive_us_tim()  # Execute the function to start listening for US TIM messages
