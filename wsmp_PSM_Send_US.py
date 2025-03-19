# PSM (Personal Safety Message)


# PSM messages are used by vulnerable road users (pedestrians, cyclists)
# to broadcast their location and movement for safety.

import time
import json

from pycmssdk import (
    create_cms_api,
    WsmpSendData,
    WsmpTxHdrInfo,
    RadioTxParams,
    MacAddr,
    SecDot2TxInfo,
    SecDot2TxSignInfo,
    SignMethod,
)

V2X_STACK_IP = "192.168.1.54"
PSID = 107  # PSID for US PSM messages

def send_us_psm():
    """
    This function continuously sends Personal Safety Messages (PSM).
    PSM messages help pedestrians and cyclists share their location with nearby vehicles.
    """
    with create_cms_api(host=V2X_STACK_IP) as api:
        print("[Sender] Connected to V2X Stack for US PSM...")

        send_data = WsmpSendData(
            radio=RadioTxParams(
                interface_id=1,
                dest_address=MacAddr(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF),
                datarate=6,
                tx_power=20,
                expiry_time=1000,
            ),
            wsmp_hdr=WsmpTxHdrInfo(psid=PSID),
            security=SecDot2TxInfo(sign_info=SecDot2TxSignInfo(
                sign_method=SignMethod.SIGN_METH_SIGN_CERT,
                psid=PSID
            )),
        )

        while True:
            psm_payload = {
                "device_id": "pedestrian_001",  # Unique ID for the wearable device
                "user_type": "pedestrian",  # Indicates a pedestrian (could also be cyclist)
                "latitude": 52001000,  # Current latitude (microdegrees)
                "longitude": 13001000,  # Current longitude (microdegrees)
                "speed": 0,   # Walking speed (in mm/s) can be low
                "heading": 0,  # Direction of movement (if available)
                "timestamp": int(time.time() * 1000),
            }

            raw_message = json.dumps(psm_payload).encode("utf-8")

            try:
                api.wsmp_send(send_data, buffer=raw_message)
                print(f"[Sender] Sent US PSM: {psm_payload}")
            except Exception as e:
                print(f"[Sender] Error sending US PSM: {e}")

            time.sleep(1)

if __name__ == "__main__":
    send_us_psm()

'''

Example of PSM(Bit complicated one but yes one of the major use case too)

For example a cyclist wearing a connected device that sends US
PSM messages. Nearby vehicles receive these messages and can adjust their behavior to 
ensure the cyclist's safety, reducing the risk of accidents.

'''