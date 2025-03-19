# This script listens for incoming US Probe Data Messages (PDM)
# It logs all received messages to a file for further analysis.

import time
import json

from pycmssdk import (
    create_cms_api,         # Connects to the V2X stack
    WsmpRxNotifData,        # Structure for received WSMP messages
)

V2X_STACK_IP = "192.168.1.54"       # V2X device IP address
LOG_FILE = "received_us_pdm.log"    # File to store received PDM messages

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    Callback function triggered when a US PDM message is received.
    It decodes the message and logs it.
    """
    try:
        message = json.loads(buffer.decode("utf-8"))
        print("Received US PDM:", message)
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")
    except Exception as e:
        print(f"Error decoding US PDM: {e}")

def receive_us_pdm():
    """
    This function subscribes to US PDM messages and continuously listens.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US PDM messages...")
        psid = 109
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  # PSID 109 for US PDM

        while True:
            time.sleep(1)

if __name__ == "__main__":
    receive_us_pdm()
