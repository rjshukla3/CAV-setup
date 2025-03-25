# rsu_wait_and_send.py

"""
This script runs on a Roadside Unit (RSU).
It waits for an On-Board Unit (OBU) to send a "ready" message,
then transmits pre-defined crack images (with metadata) over WSMP,
chunked in base64 format to stay within WSMP limits.
"""

#
import time              # For timestamps and sleep delays
import json              # To serialize Python dicts into JSON for WSMP payload
import base64            # For converting image bytes to base64 string (text-safe)
import os                # For file system operations (like checking if file exists)
import logging           # For consistent output with timestamps
from PIL import Image    # For image conversion, resizing, compression
import io                # For in-memory byte storage (no temp file needed)
from threading import Event  # Used to pause until OBU is detected

# Commsignia V2X SDK Imports 
# T
from pycmssdk import (
    create_cms_api,         # Establish connection to the Commsignia V2X stack
    WsmpRxNotifData,        # Structure for incoming WSMP messages
    WsmpSendData,           # Structure to configure outgoing WSMP messages
    WsmpTxHdrInfo,          # Header info for WSMP transmission
    RadioTxParams,          # Radio parameters like interface, power, data rate
    MacAddr,                # MAC address helper
    SecDot2TxInfo,          # Security wrapper (1609.2 standard)
    SecDot2TxSignInfo,      # Digital signature info
    SignMethod              # Signing method enum
)

# Configuration Parameters 

V2X_STACK_IP = "192.168.1.54"      # IP of RSU or device running Commsignia stack
IMAGE_SEND_PSID = 200              # PSID used to send image data
OBU_SIGNAL_PSID = 201              # PSID to receive "I'm ready" signal from OBU
CHUNK_SIZE = 1024                  # Size of each chunk (safe for WSMP payload limits)
READY_EVENT = Event()              # Threading flag set when OBU is detected

# Set up logging to include timestamps in output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Pre-defined image files and their metadata (normally this would be dynamic or from a database/ real time)
CRACK_DATA = [
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch0_aug1 (1).png", "info": {"severity": "high", "location": [52.0001, 13.0001], "type": "longitudinal"}},
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch0_aug1.png", "info": {"severity": "medium", "location": [52.0002, 13.0002], "type": "transverse"}},
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch0.png", "info": {"severity": "low", "location": [52.0003, 13.0003], "type": "alligator"}},
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch1_aug1.png", "info": {"severity": "high", "location": [52.0004, 13.0004], "type": "edge"}},
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch1.png", "info": {"severity": "medium", "location": [52.0005, 13.0005], "type": "block"}},
    {"file": "/Users/seaslab/Desktop/Rishabh Shukla/RSU/0001-3_patch2_aug2.png", "info": {"severity": "low", "location": [52.0006, 13.0006], "type": "slippage"}},
]
# here image location/path is defined as it is in MACBOOK


def current_millis() -> int:
    """
    Return current time in milliseconds.
    Used to calculate delay between sending and receiving.
    """
    return int(time.time() * 1000)


def compress_image_to_base64(image_path: str) -> str:
    """
    Convert image to grayscale, resize, compress as JPEG,
    then encode the compressed image into base64 text string.
    This makes it easy to send over WSMP (which handles text data well).
    """
    try:
        img = Image.open(image_path).convert("L").resize((256, 256))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=30)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logging.error(f"Could not compress image {image_path}: {e}")
        return ""


def send_images(api):
    """
    Sends all images in CRACK_DATA using WSMP in chunks.
    Each image is divided into 1024-byte chunks and sent one at a time.
    The first chunk includes the crack metadata (severity, location, etc.).
    """
    # Configure WSMP transmission settings
    send_data = WsmpSendData(
        radio=RadioTxParams(
            interface_id=1,                                 # Usually 1 (default radio interface)
            dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),  # Broadcast
            datarate=6,                                     # Data rate in Mbps
            tx_power=20,                                    # Transmission power (dBm)
            expiry_time=1000                                # Message expiry time in milliseconds
        ),
        wsmp_hdr=WsmpTxHdrInfo(psid=IMAGE_SEND_PSID),       # Target PSID
        security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
            sign_method=SignMethod.SIGN_METH_SIGN_CERT,     # Use certificate to sign
            psid=IMAGE_SEND_PSID
        )),
    )

    for idx, entry in enumerate(CRACK_DATA):
        image_id = f"crack_img_{idx + 1}"                   # Unique ID for each image
        img_path = entry["file"]
        crack_info = entry["info"]
        crack_info["sent_time"] = current_millis()          # Include send time for delay tracking

        if not os.path.exists(img_path):
            logging.warning(f"Image not found: {img_path}")
            continue

        b64_img = compress_image_to_base64(img_path)
        if not b64_img:
            continue

        total_chunks = (len(b64_img) + CHUNK_SIZE - 1) // CHUNK_SIZE  # Total number of chunks

        # Send all chunks one-by-one
        for chunk_num in range(total_chunks):
            chunk = b64_img[chunk_num * CHUNK_SIZE:(chunk_num + 1) * CHUNK_SIZE]

            # Metadata (crack_info) is only sent in the first chunk
            payload = {
                "image_id": image_id,
                "chunk_number": chunk_num,
                "total_chunks": total_chunks,
                "crack_info": crack_info if chunk_num == 0 else {},
                "data": chunk
            }

            try:
                raw_msg = json.dumps(payload).encode("utf-8")
                api.wsmp_send(send_data, buffer=raw_msg)
                logging.info(f"Sent {image_id} chunk {chunk_num + 1}/{total_chunks}")
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Failed to send chunk {chunk_num} of {image_id}: {e}")


def obu_signal_callback(key: int, data: WsmpRxNotifData, buffer: bytes):
    """
    Callback that runs when the RSU receives a WSMP message on the OBU_SIGNAL_PSID.
    It checks if the message includes 'status': 'ready' — meaning OBU is ready to receive.
    If so, it sets the READY_EVENT, which triggers image sending.
    """
    try:
        msg = json.loads(buffer.decode("utf-8"))
        if msg.get("status") == "ready":
            logging.info(f"OBU ready message received from: {msg.get('obu_id')}")
            READY_EVENT.set()
    except Exception as e:
        logging.error(f"Failed to decode OBU signal: {e}")


def wait_and_send():
    """
    Main loop that waits for OBU detection, then sends images.
    After sending, it clears the flag and waits again.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        logging.info("RSU initialized. Waiting for OBU...")

        # Start listening for OBU ready messages
        api.wsmp_rx_subscribe(OBU_SIGNAL_PSID, obu_signal_callback)

        while True:
            READY_EVENT.wait()              # Wait until OBU is detected
            logging.info("OBU in range. Sending images...")
            send_images(api)
            READY_EVENT.clear()            # Clear flag to wait for next OBU
            logging.info("Image transmission complete. Waiting again...")


def main():
    """Entry point of the RSU script."""
    wait_and_send()


if __name__ == "__main__":
    main()
