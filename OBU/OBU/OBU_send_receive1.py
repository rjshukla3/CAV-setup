# obu_send_and_receive.py

"""
This script runs on an On-Board Unit (OBU).
It has two main tasks:
1. Firstly continously sends an "I'm here" message to let the RSU know it is ready.
2. Listens for crack image data from the RSU, reassembles and saves it.
Each received image is logged along with its crack information and delay.
"""

import time              # Used to get timestamps and delays
import json              # For encoding/decoding JSON messages
import base64            # For encoding/decoding image data
import os                # To create folders and save files
import logging           # For clear logging messages
from threading import Thread       # To run sender and receiver at the same time
from collections import defaultdict  # To collect image chunks by image ID

# Commsignia SDK Imports  
from pycmssdk import (
    create_cms_api,         # Connects to the Commsignia V2X device
    WsmpRxNotifData,        # Used to receive WSMP messages
    WsmpSendData,           # Used to send WSMP messages
    WsmpTxHdrInfo,          # Adds headers to WSMP messages
    RadioTxParams,          # Sets up transmission parameters
    MacAddr,                # For defining destination MAC address
    SecDot2TxInfo,          # Wraps security info
    SecDot2TxSignInfo,      # Signature details for security
    SignMethod              # Signing method type (cert-based)
)

# Configuration Variables 

V2X_STACK_IP = "192.168.1.54"      # IP address of OBU or V2X device
SEND_PSID = 201                    # PSID for announcing presence to RSU
RECEIVE_PSID = 200                 # PSID to receive crack images
OUTPUT_DIR = "received_images"     # Folder to save incoming images
LOG_FILE = "crack_log.csv"         # CSV file to log crack details and timing

# These will store incoming image data temporarily
CHUNK_STORE = defaultdict(dict)
METADATA_STORE = {}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def current_millis() -> int:
    """Returns the current time in milliseconds."""
    return int(time.time() * 1000)


def announce_obu():
    """
    Runs in the background and sends a 'ready' message to RSU every 2 seconds.
    This tells the RSU the OBU is present and ready to receive data.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcast
                datarate=6,
                tx_power=20,
                expiry_time=1000,
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=SEND_PSID),
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,
                psid=SEND_PSID
            )),
        )

        while True:
            message = {
                "obu_id": "obu_123",
                "status": "ready"
            }

            try:
                raw = json.dumps(message).encode("utf-8")
                api.wsmp_send(send_data, buffer=raw)
                logging.info("Sent OBU ready signal to RSU.")
            except Exception as e:
                logging.error(f"Failed to send ready signal: {e}")

            time.sleep(2)  # Wait 2 seconds before sending again


def save_and_log_image(image_id, base64_data, crack_info, received_time_ms):
    """
    Saves the reconstructed image and logs crack metadata to CSV.
    Also logs the time delay between RSU sending and OBU receiving.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image_path = os.path.join(OUTPUT_DIR, f"{image_id}.jpg")

    # Convert base64 back to binary image
    try:
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
    except Exception as e:
        logging.error(f"Failed to save image: {e}")
        return

    # Calculate delay from RSU send time
    sent_time = crack_info.get("sent_time", 0)
    delay = received_time_ms - sent_time if sent_time else "N/A"

    # If CSV file doesn't exist, write headers
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as log_file:
            log_file.write("image_id,severity,location,type,sent_time,received_time,delay_ms\n")

    # Append crack info and delay to log file
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(
                f"{image_id},{crack_info.get('severity','')},{crack_info.get('location','')},"
                f"{crack_info.get('type','')},{sent_time},{received_time_ms},{delay}\n"
            )
        logging.info(f"Saved {image_id}.jpg and logged delay: {delay} ms")
    except Exception as e:
        logging.error(f"Could not write to log file: {e}")


def receive_data():
    """
    Listens for crack image chunks sent from the RSU.
    Reconstructs the image once all chunks are received and logs the crack info.
    """
    def callback(key: int, data: WsmpRxNotifData, buffer: bytes):
        try:
            message = json.loads(buffer.decode("utf-8"))

            image_id = message["image_id"]
            chunk_num = message["chunk_number"]
            total_chunks = message["total_chunks"]
            crack_info = message.get("crack_info", {})
            chunk_data = message["data"]

            # Store chunk by number
            CHUNK_STORE[image_id][chunk_num] = chunk_data

            # Store metadata only from the first chunk
            if crack_info:
                METADATA_STORE[image_id] = crack_info

            logging.info(f"Received chunk {chunk_num + 1}/{total_chunks} for {image_id}")

            # If all chunks are received, reassemble image
            if len(CHUNK_STORE[image_id]) == total_chunks:
                full_image = ''.join(CHUNK_STORE[image_id][i] for i in range(total_chunks))
                crack_info = METADATA_STORE.get(image_id, {})
                save_and_log_image(image_id, full_image, crack_info, current_millis())

                # Clean up memory
                del CHUNK_STORE[image_id]
                METADATA_STORE.pop(image_id, None)

        except Exception as e:
            logging.error(f"Error processing received chunk: {e}")

    # Connect and start listening
    with create_cms_api(host=V2X_STACK_IP) as api:
        api.wsmp_rx_subscribe(RECEIVE_PSID, callback)
        logging.info("OBU is listening for incoming crack image data...")

        # Keep the process running
        while True:
            time.sleep(1)


def main():
    """
    Starts both the announce and receive functions.
    One runs in the background, the other in the foreground.
    """
    logging.info("OBU started. Announcing and receiving...")
    Thread(target=announce_obu, daemon=True).start()
    receive_data()


if __name__ == "__main__":
    main()
