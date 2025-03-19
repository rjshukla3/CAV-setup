# This script listens for incoming US PSM (Personal Safety Message) messages.
# It logs all received messages to a file for analysis.

import time
import json

from pycmssdk import (
    create_cms_api,
    WsmpRxNotifData,
)

V2X_STACK_IP = "192.168.1.54"
LOG_FILE = "received_us_psm.log"

def wsmp_rx_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    Callback function that processes received US PSM messages.
    """
    try:
        message = json.loads(buffer.decode("utf-8"))
        print("Received US PSM:", message)
        with open(LOG_FILE, "a") as file:
            json.dump(message, file)
            file.write("\n")
    except Exception as e:
        print(f"Error decoding US PSM: {e}")

def receive_us_psm():
    """
    This function subscribes to US PSM messages and continuously listens.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Receiver] Subscribed to US PSM messages...")
        psid = 107
        api.wsmp_rx_subscribe(psid, wsmp_rx_callback)  # PSID 107 for US PSM

        while True:
            time.sleep(1)

if __name__ == "__main__":
    receive_us_psm()
