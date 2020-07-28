from inkbird.client import InkBirdClient
import bluepy
import time
import os

import logging

logger = logging.getLogger("inkbird")
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
)

if __name__ == "__main__":
    address = os.environ.get("INKBIRD_ADDRESS")
    client = InkBirdClient(address=address)

    while True:
        try:
            logger.info(f"Connecting to {address}")
            client.connect()
            client.login()
            client.enable_data()
            client.enable_battery()

            logger.debug("Starting Loop")
            while True:
                try:
                    if client.client.waitForNotifications(1.0):
                        continue
                except bluepy.btle.BTLEInternalError:
                    pass
        except bluepy.btle.BTLEDisconnectError:
            time.sleep(5)
            logger.info(f"Reconnecting to {address}")
