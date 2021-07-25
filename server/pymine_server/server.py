#!/usr/bin/env python3
#
#   The server!
#
#  A part of denosawr/pymine

import asyncio
import threading

from typing import cast, Optional

from .connectors import (
    MinecraftConnector,
    WSBridgeConnector,
    HTTPConnector,
    Publisher,
)
from .utils.logging import getLogger
from .tray import create_tray

from pystray import Icon

log = getLogger("server")


def start_server(icon: Optional[Icon] = None, port: int = 19131) -> None:
    log.info("Server started.")

    # threadsafe alternative to asyncio.get_event_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop = cast(asyncio.BaseEventLoop, loop)  # 'hide' type casting errors

    publisher = Publisher()
    recv_queue = asyncio.Queue()

    minecraft_connection = MinecraftConnector(publisher, recv_queue, port=port)
    ws_connection = WSBridgeConnector(publisher, recv_queue)
    http_connector = HTTPConnector(publisher, recv_queue)

    try:
        minecraft_connection.start(loop)
        ws_connection.start(loop)
        http_connector.start(loop)

        log.debug("Starting event loop...")
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt, closing...")

    if icon:
        icon.stop()


def create_server_thread(icon: Icon, port: int = 19131) -> threading.Thread:
    t = threading.Thread(target=start_server, args=(icon, port,), daemon=True,)
    t.start()
    return t


if __name__ == "__main__":
    start_server()
