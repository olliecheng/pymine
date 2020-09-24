#!/usr/bin/env python3
#
#   The server!
#
#  A part of denosawr/pymine

import asyncio

from typing import List, Dict, Tuple, Sequence

from pymine.server.connectors import MinecraftConnector, WSBridgeConnector, Publisher
from pymine.utils.logging import getLogger

log = getLogger("main")


def start_server(port: int = 19131):
    log.info("Server started.")

    publisher = Publisher()
    recv_queue = asyncio.Queue()

    minecraft_connection = MinecraftConnector(publisher, recv_queue, port=19131)
    ws_connection = WSBridgeConnector(publisher, recv_queue)

    loop = asyncio.get_event_loop()
    try:
        minecraft_connection.start(loop)
        ws_connection.start(loop)

        log.debug("Starting event loop...")
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt, closing...")


if __name__ == "__main__":
    start_server()
